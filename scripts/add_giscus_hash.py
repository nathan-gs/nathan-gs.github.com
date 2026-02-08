#!/usr/bin/env python3
"""
Add giscus SHA-1 hash to existing GitHub Discussions.

Giscus strict mode requires a SHA-1 hash comment in the discussion body
to verify the match. This script adds that hash to migrated discussions.

Usage:
    python add_giscus_hash.py --token YOUR_GITHUB_TOKEN [--dry-run]
"""

import argparse
import hashlib
import requests
import time

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
REPO_OWNER = "nathan-gs"
REPO_NAME = "nathan-gs.github.com"


def get_all_discussions(token):
    """Fetch all discussions from the repository."""
    discussions = []
    cursor = None
    
    while True:
        query = """
        query($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                discussions(first: 50, after: $cursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        title
                        number
                        body
                    }
                }
            }
        }
        """
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            GITHUB_GRAPHQL_URL,
            json={
                "query": query,
                "variables": {
                    "owner": REPO_OWNER,
                    "name": REPO_NAME,
                    "cursor": cursor
                }
            },
            headers=headers
        )
        
        data = response.json()
        
        if 'errors' in data:
            print(f"Error fetching discussions: {data['errors']}")
            break
        
        nodes = data['data']['repository']['discussions']['nodes']
        discussions.extend(nodes)
        
        page_info = data['data']['repository']['discussions']['pageInfo']
        if page_info['hasNextPage']:
            cursor = page_info['endCursor']
        else:
            break
    
    return discussions


def update_discussion_body(token, discussion_id, new_body):
    """Update a discussion's body."""
    mutation = """
    mutation($discussionId: ID!, $body: String!) {
        updateDiscussion(input: {
            discussionId: $discussionId,
            body: $body
        }) {
            discussion {
                id
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        GITHUB_GRAPHQL_URL,
        json={
            "query": mutation,
            "variables": {
                "discussionId": discussion_id,
                "body": new_body
            }
        },
        headers=headers
    )
    
    return response.json()


def compute_giscus_hash(pathname):
    """Compute the SHA-1 hash that giscus expects."""
    # Giscus computes SHA-1 of the search term (pathname)
    return hashlib.sha1(pathname.encode('utf-8')).hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description='Add giscus SHA-1 hash to GitHub Discussions'
    )
    parser.add_argument(
        '--token', '-t',
        required=True,
        help='GitHub Personal Access Token'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    print("Fetching discussions...")
    discussions = get_all_discussions(args.token)
    print(f"Found {len(discussions)} discussions\n")
    
    updated = 0
    skipped = 0
    
    for d in discussions:
        title = d['title']
        body = d['body'] or ''
        
        # Skip discussions starting with post/ or blog/
        if title.startswith('post/') or title.startswith('blog/'):
            print(f"  Skipping (old format): #{d['number']} - {title}")
            skipped += 1
            continue
        
        # Skip if already has giscus hash
        if '<!-- sha1:' in body:
            print(f"  Skipping (already has hash): #{d['number']} - {title}")
            skipped += 1
            continue
        
        # The pathname that giscus searches for (title is the pathname)
        pathname = title
        sha1_hash = compute_giscus_hash(pathname)
        
        # Giscus expects the hash at the beginning of the body
        hash_comment = f"<!-- sha1: {sha1_hash} -->\n"
        new_body = hash_comment + body
        
        print(f"#{d['number']}: {title}")
        print(f"  Hash: {sha1_hash}")
        
        if args.dry_run:
            print(f"  [DRY RUN] Would add hash to body")
        else:
            result = update_discussion_body(args.token, d['id'], new_body)
            
            if 'errors' in result:
                error_msg = str(result['errors'])
                print(f"  ERROR: {error_msg}")
                
                if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                    print(f"  Rate limited, waiting 60s...")
                    time.sleep(60)
                    result = update_discussion_body(args.token, d['id'], new_body)
                    if 'errors' in result:
                        print(f"  Retry failed: {result['errors']}")
                    else:
                        print(f"  ✓ Hash added (after retry)")
                        updated += 1
            else:
                print(f"  ✓ Hash added")
                updated += 1
            
            time.sleep(2)  # Rate limiting
        
        print()
    
    print(f"\nSummary: {updated} updated, {skipped} skipped")
    
    if args.dry_run:
        print("\n[DRY RUN] No changes made. Run without --dry-run to apply.")


if __name__ == '__main__':
    main()
