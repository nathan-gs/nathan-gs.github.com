#!/usr/bin/env python3
"""
Migrate historical analytics data from Piwik PRO (free tier) to Matomo (self-hosted).

Piwik PRO free tier limits: up to 500k actions/month, supports Raw Data API.

How it works:
1. Authenticates with Piwik PRO via OAuth2 client credentials
2. Fetches raw sessions and events from Piwik PRO Raw Data API (paginated)
3. Replays each hit to Matomo via the Tracking HTTP API

Prerequisites:
  - Piwik PRO client ID and client secret (Settings → Apps → {app} → API credentials)
  - Piwik PRO account domain (e.g. yourname.piwik.pro) and Site ID (UUID)
  - Matomo token_auth (Settings → Personal → Security → Auth token)
  - Matomo site ID and base URL

Usage:
    python migrate_piwikpro_to_matomo.py \\
        --piwikpro-url https://yourname.piwik.pro \\
        --piwikpro-site-id <UUID> \\
        --piwikpro-client-id <CLIENT_ID> \\
        --piwikpro-client-secret <CLIENT_SECRET> \\
        --matomo-url https://t.nathan.gs \\
        --matomo-site-id 1 \\
        --matomo-token <TOKEN_AUTH> \\
        --matomo-admin-token <SUPER_USER_TOKEN_AUTH> \
        --start-date 2024-01-01 \
        --end-date 2025-01-01

Notes:
    --matomo-token       Regular auth token (used for tracking API bulk inserts)
    --matomo-admin-token Super User token (required for archive invalidation).
                         Find it in Matomo → Administration → System → General Settings
                         or create a Super User account and copy its token_auth.
                         If omitted, falls back to --matomo-token (will 401 unless it
                         already has Super User privileges).

Optional flags:
    --dry-run       Fetch from Piwik PRO but do not send to Matomo
    --batch-size    Number of hits per Matomo bulk request (default: 50)
    --delay         Seconds to sleep between bulk requests (default: 0.5)
    --session-limit Max sessions to fetch per day window (default: unlimited)
"""

import argparse
import sys
import time
import json
import logging
from datetime import date, timedelta, datetime, timezone
from urllib.parse import quote_plus

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Piwik PRO helpers
# ---------------------------------------------------------------------------

PIWIKPRO_TOKEN_PATH = "/auth/token"
PIWIKPRO_SESSIONS_PATH = "/api/analytics/v1/sessions/"
PIWIKPRO_EVENTS_PATH = "/api/analytics/v1/events/"

# Additional columns to request from Piwik PRO sessions endpoint
# (session_id, visitor_id, timestamp are returned by default)
SESSION_COLUMNS = [
    "location_country_name",
    "location_city_name",
    "browser_name",
    "browser_version",
    "operating_system",
    "device_type",
    "resolution",
    "browser_language_iso639",
    "referrer_url",
    "source",
    "medium",
    "session_total_time",
    "session_total_goal_conversions",
    "visitor_returning",
]

# Additional columns to request from Piwik PRO events endpoint
# (session_id, event_id, visitor_id, timestamp are returned by default)
EVENT_COLUMNS = [
    "event_type",
    "event_url",
    "event_title",
    "time_on_page",
    "custom_event_category",
    "custom_event_action",
    "custom_event_name",
    "custom_event_value",
]


def _http_session() -> requests.Session:
    """Return a requests Session with automatic retries for all methods."""
    s = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=1.0,
        backoff_max=30,                  # cap individual wait at 30s (1, 2, 4, 8, 16 → max 30)
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=None,            # None = retry ALL HTTP methods including POST (urllib3 2.x)
        respect_retry_after_header=True,  # honour Retry-After on 429
        connect=3,
        read=3,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


def get_piwikpro_token(base_url: str, client_id: str, client_secret: str, http: requests.Session | None = None) -> tuple[str, float]:
    """Obtain an OAuth2 Bearer token from Piwik PRO.
    Returns (access_token, expiry_timestamp).
    """
    session = http or _http_session()
    url = base_url.rstrip("/") + PIWIKPRO_TOKEN_PATH
    resp = session.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    token = body.get("access_token")
    if not token:
        raise ValueError(f"No access_token in response: {resp.text}")
    expires_in = int(body.get("expires_in", 1800))
    expiry = time.monotonic() + expires_in - 60  # refresh 60s before actual expiry
    log.info("Obtained Piwik PRO token (expires in %ss)", expires_in)
    return token, expiry


def fetch_piwikpro_raw(
    http: requests.Session,
    base_url: str,
    token: str,
    site_id: str,
    path: str,
    columns: list[str],
    date_from: str,
    date_to: str,
    limit: int = 1000,
) -> list[dict]:
    """
    Fetch all rows from a Piwik PRO sessions/events endpoint for a date range.
    Handles pagination via offset/limit cursor and converts rows to dicts using
    column names returned in meta.columns.
    """
    url = base_url.rstrip("/") + path
    headers = {"Authorization": f"Bearer {token}"}

    rows: list[dict] = []
    offset = 0

    while True:
        payload = {
            "website_id": site_id,
            "date_from": date_from,
            "date_to": date_to,
            "columns": [{"column_id": c} for c in columns],
            "offset": offset,
            "limit": limit,
        }
        resp = http.post(url, json=payload, headers=headers, timeout=60)

        if resp.status_code == 401:
            raise PermissionError("Piwik PRO token rejected — token may have expired, re-run with fresh credentials.")
        if resp.status_code == 403:
            raise PermissionError(
                "Piwik PRO API not available on your plan or site permissions denied."
            )
        if not resp.ok:
            log.error("Piwik PRO %s error for %s: %s", resp.status_code, url, resp.text)
        resp.raise_for_status()

        data = resp.json()
        batch = data.get("data", [])
        meta = data.get("meta", {})
        meta_columns = meta.get("columns", [])
        total_count = meta.get("count", 0)

        log.debug(
            "  API response: count=%s, batch_size=%d, columns=%s",
            total_count,
            len(batch),
            meta_columns,
        )

        if not batch:
            if offset == 0:
                log.debug("  API returned 0 rows (count=%s) for %s→%s", total_count, date_from, date_to)
            break

        # Convert each row (list) to a dict using column names from meta
        for row in batch:
            if isinstance(row, list):
                rows.append({meta_columns[i]: row[i] for i in range(min(len(meta_columns), len(row)))})
            else:
                rows.append(row)

        log.debug("  fetched %d rows (total so far: %d)", len(batch), len(rows))

        if len(rows) >= total_count or len(batch) < limit:
            break
        offset += limit

    return rows


def row_to_dict(row: list, columns: list[str]) -> dict:
    """Legacy helper kept for compatibility; rows are now pre-converted to dicts."""
    return {columns[i]: row[i] for i in range(min(len(columns), len(row)))}


# ---------------------------------------------------------------------------
# Matomo helpers
# ---------------------------------------------------------------------------

MATOMO_TRACKING_PATH = "/matomo.php"


def _str(val) -> str:
    """Coerce a Piwik PRO field value to str; some columns return [id, label] lists."""
    if isinstance(val, list):
        return next((str(v) for v in val if isinstance(v, str)), str(val[-1]) if val else "")
    return str(val) if val is not None else ""


def build_matomo_hit(
    matomo_site_id: str | int,
    token_auth: str,
    session: dict,
    event: dict,
) -> dict:
    """
    Map a Piwik PRO session + event row to a Matomo Tracking API parameter dict.
    https://developer.matomo.org/api-reference/tracking-api
    """

    # Timestamp: Piwik PRO returns ISO 8601 UTC strings
    ts_raw = event.get("timestamp") or session.get("timestamp", "")
    try:
        dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        cdt = dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        cdt = None

    hit: dict = {
        "idsite": matomo_site_id,
        "rec": 1,
        "send_image": 0,
    }

    # Page URL
    url = _str(event.get("event_url") or "")
    if url:
        hit["url"] = url

    if cdt:
        hit["cdt"] = cdt

    # Visitor / session identifiers (use first 16 hex chars as cid)
    visitor_id = session.get("visitor_id") or session.get("session_id") or ""
    if visitor_id:
        # Matomo cid must be exactly 16 hex characters
        cid = visitor_id.replace("-", "")[:16].lower()
        hit["cid"] = cid

    # Geo / language
    if session.get("location_country_name"):
        hit["country"] = _str(session["location_country_name"])
    if session.get("location_city_name"):
        hit["city"] = _str(session["location_city_name"])
    if session.get("browser_language_iso639"):
        hit["lang"] = _str(session["browser_language_iso639"])

    # Screen resolution
    if session.get("resolution"):
        hit["res"] = _str(session["resolution"])

    # Referrer
    if session.get("referrer_url"):
        hit["urlref"] = _str(session["referrer_url"])

    # User agent (reconstructed from browser + OS)
    # Some Piwik PRO columns return [id, label] lists — _str() handles that
    ua_parts = []
    browser = _str(session.get("browser_name"))
    version = _str(session.get("browser_version"))
    os_name = _str(session.get("operating_system"))
    if browser:
        ua_parts.append(f"{browser}/{version}" if version else browser)
    if os_name:
        ua_parts.append(f"({os_name})")
    if ua_parts:
        hit["ua"] = " ".join(ua_parts)

    # Page title (event_title for all event types in Piwik PRO)
    title = _str(event.get("event_title") or "")
    if title:
        hit["action_name"] = title

    # Custom event tracking (non-pageview events)
    event_type = _str(event.get("event_type") or "")
    if event_type and event_type.lower() not in ("pageview", "page_view", ""):
        hit["e_c"] = _str(event.get("custom_event_category")) or event_type
        if event.get("custom_event_action"):
            hit["e_a"] = _str(event["custom_event_action"])
        if event.get("custom_event_name"):
            hit["e_n"] = _str(event["custom_event_name"])
        if event.get("custom_event_value") is not None:
            hit["e_v"] = event["custom_event_value"]

    # Time on page (in seconds)
    if event.get("time_on_page") is not None:
        hit["gt_ms"] = int(float(event["time_on_page"]) * 1000)

    return hit


def send_matomo_bulk(
    http: requests.Session,
    matomo_url: str,
    token_auth: str,
    hits: list[dict],
    dry_run: bool = False,
    max_attempts: int = 3,
) -> None:
    """Send a list of hits to Matomo via the bulk tracking endpoint."""
    if dry_run:
        log.info("[dry-run] Would send %d hits to Matomo", len(hits))
        return

    url = matomo_url.rstrip("/") + MATOMO_TRACKING_PATH
    payload = {
        "requests": [
            "?" + "&".join(f"{k}={quote_plus(str(v))}" for k, v in hit.items())
            for hit in hits
        ],
        "token_auth": token_auth,  # only in envelope, not per-hit
    }

    for attempt in range(1, max_attempts + 1):
        try:
            resp = http.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            if result.get("status") != "success":
                log.warning("Matomo bulk response: %s", result)
            else:
                log.debug("Matomo accepted %d hits", len(hits))
            return
        except requests.RequestException as exc:
            if attempt == max_attempts:
                raise
            wait = 2 ** attempt
            log.warning("Matomo send failed (attempt %d/%d): %s — retrying in %ds",
                        attempt, max_attempts, exc, wait)
            time.sleep(wait)


def invalidate_matomo_archives(
    http: requests.Session,
    matomo_url: str,
    admin_token: str,
    site_id: int,
    start: date,
    end: date,
) -> None:
    """
    Invalidate Matomo report cache for each month in the date range so that
    imported historical hits appear in reports.
    Calls CoreAdminHome.invalidateArchivedReports for each YYYY-MM in range.
    Requires a Super User token_auth (Administration → Super Users → token_auth).
    """
    url = matomo_url.rstrip("/") + "/index.php"

    # Collect unique months, expressed as first-of-month dates (YYYY-MM-DD)
    months: list[str] = []
    seen: set[str] = set()
    current = start.replace(day=1)
    end_month = end.replace(day=1)
    while current <= end_month:
        key = current.strftime("%Y-%m-%d")
        if key not in seen:
            seen.add(key)
            months.append(key)
        # advance to next month
        next_month = current.month % 12 + 1
        next_year = current.year + (1 if current.month == 12 else 0)
        current = current.replace(year=next_year, month=next_month, day=1)

    # Send all months in a single API call; period=month + cascadeDown=1 covers days/weeks too
    payload = {
        "module": "API",
        "method": "CoreAdminHome.invalidateArchivedReports",
        "idSites": site_id,
        "dates": ",".join(months),
        "period": "month",
        "cascadeDown": 1,
        "format": "JSON",
        "token_auth": admin_token,
    }
    try:
        resp = http.post(url, data=payload, timeout=60)
        if resp.status_code == 401:
            raise requests.HTTPError(
                f"401 Unauthorized — response body: {resp.text[:300]}",
                response=resp,
            )
        resp.raise_for_status()
        log.info("Invalidated Matomo archives for: %s", ", ".join(months))
    except requests.RequestException as exc:
        log.warning("Failed to invalidate archives: %s", exc)




def date_range(start: date, end: date):
    """Yield each day from start (inclusive) to end (exclusive)."""
    current = start
    while current < end:
        yield current
        current += timedelta(days=1)


def migrate(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    http = _http_session()

    # Authenticate with Piwik PRO
    log.info("Authenticating with Piwik PRO at %s ...", args.piwikpro_url)
    token, token_expiry = get_piwikpro_token(
        args.piwikpro_url, args.piwikpro_client_id, args.piwikpro_client_secret, http
    )

    def _fresh_token() -> str:
        """Return current token, refreshing if it's about to expire."""
        nonlocal token, token_expiry
        if time.monotonic() >= token_expiry:
            log.info("Token expiring soon — refreshing...")
            token, token_expiry = get_piwikpro_token(
                args.piwikpro_url, args.piwikpro_client_id, args.piwikpro_client_secret, http
            )
        return token

    start = date.fromisoformat(args.start_date)
    end = date.fromisoformat(args.end_date)
    log.info(
        "Migrating %s → %s  |  site %s → Matomo site %s",
        start,
        end,
        args.piwikpro_site_id,
        args.matomo_site_id,
    )

    total_hits_sent = 0

    for day in date_range(start, end):
        date_str = day.isoformat()
        next_day_str = (day + timedelta(days=1)).isoformat()

        log.info("Processing %s ...", date_str)

        # --- Fetch sessions ---
        raw_sessions = fetch_piwikpro_raw(
            http,
            args.piwikpro_url,
            _fresh_token(),
            args.piwikpro_site_id,
            PIWIKPRO_SESSIONS_PATH,
            SESSION_COLUMNS,
            date_str,
            next_day_str,
        )
        sessions_by_id: dict[str, dict] = {}
        for s in raw_sessions:
            sessions_by_id[s.get("session_id", "")] = s

        if not sessions_by_id:
            log.info("  No sessions on %s (API returned %d rows), skipping.", date_str, len(raw_sessions))
            continue

        log.info("  Found %d sessions", len(sessions_by_id))

        # --- Fetch events ---
        raw_events = fetch_piwikpro_raw(
            http,
            args.piwikpro_url,
            _fresh_token(),
            args.piwikpro_site_id,
            PIWIKPRO_EVENTS_PATH,
            EVENT_COLUMNS,
            date_str,
            next_day_str,
        )
        log.info("  Found %d events", len(raw_events))

        # --- Build + send hits ---
        batch: list[dict] = []
        for event in raw_events:
            session = sessions_by_id.get(event.get("session_id", ""), {})
            hit = build_matomo_hit(
                args.matomo_site_id,
                args.matomo_token,
                session,
                event,
            )
            # Skip if no URL (can't track a hit without a URL)
            if not hit.get("url"):
                continue
            batch.append(hit)

            if len(batch) >= args.batch_size:
                send_matomo_bulk(http, args.matomo_url, args.matomo_token, batch, args.dry_run)
                total_hits_sent += len(batch)
                batch = []
                time.sleep(args.delay)

        if batch:
            send_matomo_bulk(http, args.matomo_url, args.matomo_token, batch, args.dry_run)
            total_hits_sent += len(batch)
            time.sleep(args.delay)

    log.info(
        "Done. %s %d hits total.",
        "[dry-run]" if args.dry_run else "Sent",
        total_hits_sent,
    )

    if not args.dry_run and not args.no_invalidate:
        admin_token = args.matomo_admin_token or args.matomo_token
        log.info("Invalidating Matomo report archives for imported period...")
        invalidate_matomo_archives(
            http, args.matomo_url, admin_token, args.matomo_site_id, start, end
        )
        log.info("Archive invalidation complete. Reports will rebuild on next access.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Migrate Piwik PRO (free) history to Matomo (self-hosted).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    pp = p.add_argument_group("Piwik PRO (not needed with --invalidate-only)")
    pp.add_argument("--piwikpro-url", help="e.g. https://yourname.piwik.pro")
    pp.add_argument("--piwikpro-site-id", help="Site UUID from Piwik PRO")
    pp.add_argument("--piwikpro-client-id")
    pp.add_argument("--piwikpro-client-secret")

    mt = p.add_argument_group("Matomo")
    mt.add_argument("--matomo-url", required=True, help="e.g. https://t.nathan.gs")
    mt.add_argument("--matomo-site-id", default=1, type=int)
    mt.add_argument("--matomo-token", required=True, help="Matomo token_auth for tracking API")
    mt.add_argument("--matomo-admin-token",
                    help="Matomo Super User token_auth for archive invalidation "
                         "(defaults to --matomo-token if omitted)")

    p.add_argument("--start-date", required=True, help="YYYY-MM-DD (inclusive)")
    p.add_argument("--end-date", required=True, help="YYYY-MM-DD (exclusive)")
    p.add_argument("--invalidate-only", action="store_true",
                   help="Skip Piwik PRO import; only invalidate Matomo archives for the date range")
    p.add_argument("--dry-run", action="store_true", help="Fetch only, do not send to Matomo")
    p.add_argument("--no-invalidate", action="store_true",
                   help="Skip Matomo archive invalidation after import")
    p.add_argument("--verbose", action="store_true", help="Enable DEBUG logging")
    p.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Hits per Matomo bulk request",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds to sleep between Matomo bulk requests",
    )

    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.invalidate_only:
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        http = _http_session()
        start = date.fromisoformat(args.start_date)
        end = date.fromisoformat(args.end_date)
        admin_token = args.matomo_admin_token or args.matomo_token
        log.info("Invalidating Matomo archives from %s to %s ...", start, end)
        invalidate_matomo_archives(http, args.matomo_url, admin_token, args.matomo_site_id, start, end)
        log.info("Done. Reports will rebuild on next access.")
    else:
        missing = [
            f"--{name.replace('_', '-')}"
            for name in ("piwikpro_url", "piwikpro_site_id", "piwikpro_client_id", "piwikpro_client_secret")
            if not getattr(args, name)
        ]
        if missing:
            import sys
            print(f"error: the following arguments are required: {', '.join(missing)}", file=sys.stderr)
            sys.exit(2)
        migrate(args)
