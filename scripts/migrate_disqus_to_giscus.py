#!/usr/bin/env python3
"""
Migrate Disqus comments to GitHub Discussions for use with Giscus.

Prerequisites:
1. Export your Disqus comments from: https://disqus.com/admin/discussions/export/
2. Create a GitHub Personal Access Token with 'repo' and 'write:discussion' scopes
3. Enable Discussions on your repository
4. Install the giscus app on your repository

Usage:
    python migrate_disqus_to_giscus.py --export disqus_export.xml --token YOUR_GITHUB_TOKEN

The script will:
- Parse the Disqus XML export
- Create a GitHub Discussion for each thread (matching giscus pathname mapping)
- Add all comments as a single migration comment (preserving author attribution)
"""

import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse
import requests
import time
import sys

# GitHub GraphQL endpoint
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

# Repository settings - UPDATE THESE
REPO_OWNER = "nathan-gs"
REPO_NAME = "nathan-gs.github.com"
CATEGORY_NAME = "General"  # Must match your giscus category


def parse_disqus_export(xml_file):
    """Parse Disqus XML export and return threads with comments."""
    
    # Disqus uses a default namespace
    ns = {'disqus': 'http://disqus.com'}
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Build a map of thread IDs to thread info
    threads = {}
    for thread in root.findall('disqus:thread', ns):
        thread_id = thread.get('{http://disqus.com/disqus-internals}id')
        link = thread.find('disqus:link', ns)
        title = thread.find('disqus:title', ns)
        
        if link is not None and link.text:
            # Extract pathname from URL for giscus mapping
            parsed_url = urlparse(link.text)
            pathname = parsed_url.path.lstrip('/')  # Remove leading slash to match giscus
            
            threads[thread_id] = {
                'id': thread_id,
                'url': link.text,
                'pathname': pathname,
                'title': title.text if title is not None else pathname,
                'comments': []
            }
    
    # Parse comments and associate with threads
    for post in root.findall('disqus:post', ns):
        thread_ref = post.find('disqus:thread', ns)
        if thread_ref is None:
            continue
            
        thread_id = thread_ref.get('{http://disqus.com/disqus-internals}id')
        if thread_id not in threads:
            continue
        
        # Check if comment is not deleted/spam
        is_deleted = post.find('disqus:isDeleted', ns)
        is_spam = post.find('disqus:isSpam', ns)
        
        if (is_deleted is not None and is_deleted.text == 'true') or \
           (is_spam is not None and is_spam.text == 'true'):
            continue
        
        # Extract comment details
        message = post.find('disqus:message', ns)
        author = post.find('disqus:author', ns)
        created_at = post.find('disqus:createdAt', ns)
        
        author_name = "Anonymous"
        if author is not None:
            name_elem = author.find('disqus:name', ns)
            if name_elem is not None and name_elem.text:
                author_name = name_elem.text
        
        comment = {
            'author': author_name,
            'message': message.text if message is not None else '',
            'created_at': created_at.text if created_at is not None else '',
        }
        
        threads[thread_id]['comments'].append(comment)
    
    # Filter to only threads with comments and sort comments by date
    threads_with_comments = {}
    for thread_id, thread in threads.items():
        if thread['comments']:
            thread['comments'].sort(key=lambda x: x['created_at'])
            threads_with_comments[thread_id] = thread
    
    return threads_with_comments


def get_repo_id(token):
    """Get the repository ID using GraphQL."""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
            discussionCategories(first: 10) {
                nodes {
                    id
                    name
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
        json={"query": query, "variables": {"owner": REPO_OWNER, "name": REPO_NAME}},
        headers=headers
    )
    
    data = response.json()
    
    if 'errors' in data:
        print(f"Error getting repo info: {data['errors']}")
        sys.exit(1)
    
    repo_id = data['data']['repository']['id']
    
    # Find the category ID
    category_id = None
    for cat in data['data']['repository']['discussionCategories']['nodes']:
        if cat['name'] == CATEGORY_NAME:
            category_id = cat['id']
            break
    
    if not category_id:
        print(f"Error: Category '{CATEGORY_NAME}' not found in repository.")
        print("Available categories:")
        for cat in data['data']['repository']['discussionCategories']['nodes']:
            print(f"  - {cat['name']}")
        sys.exit(1)
    
    return repo_id, category_id


def create_discussion(token, repo_id, category_id, title, body):
    """Create a new GitHub Discussion."""
    mutation = """
    mutation($repoId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
        createDiscussion(input: {
            repositoryId: $repoId,
            categoryId: $categoryId,
            title: $title,
            body: $body
        }) {
            discussion {
                id
                url
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
                "repoId": repo_id,
                "categoryId": category_id,
                "title": title,
                "body": body
            }
        },
        headers=headers
    )
    
    return response.json()


def format_comments_as_markdown(comments):
    """Format Disqus comments as a markdown body for the discussion."""
    if not comments:
        return "_No comments to migrate._"
    
    lines = [
        "## Migrated Comments from Disqus",
        "",
        "_These comments were migrated from Disqus. Original authors are attributed below._",
        "",
        "---",
        ""
    ]
    
    for comment in comments:
        # Parse and format date
        date_str = comment['created_at']
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%B %d, %Y at %H:%M UTC')
        except:
            formatted_date = date_str
        
        lines.append(f"### 💬 {comment['author']}")
        lines.append(f"*{formatted_date}*")
        lines.append("")
        lines.append(f"> {comment['message']}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def migrate_threads(threads, token, dry_run=False):
    """Migrate all threads to GitHub Discussions."""
    repo_id, category_id = get_repo_id(token)
    
    print(f"\nFound {len(threads)} threads with comments to migrate.")
    print(f"Repository ID: {repo_id}")
    print(f"Category ID: {category_id}")
    print("")
    
    for thread_id, thread in threads.items():
        pathname = thread['pathname']
        title = pathname  # Giscus uses pathname as title with pathname mapping
        comment_count = len(thread['comments'])
        
        print(f"Processing: {pathname} ({comment_count} comments)")
        
        if dry_run:
            print(f"  [DRY RUN] Would create discussion: {title}")
            continue
        
        body = format_comments_as_markdown(thread['comments'])
        
        result = create_discussion(token, repo_id, category_id, title, body)
        
        if 'errors' in result:
            print(f"  Error: {result['errors']}")
        else:
            url = result['data']['createDiscussion']['discussion']['url']
            print(f"  Created: {url}")
        
        # Rate limiting - be nice to GitHub API
        time.sleep(1)
    
    print("\nMigration complete!")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Disqus comments to GitHub Discussions for Giscus'
    )
    parser.add_argument(
        '--export', '-e',
        required=True,
        help='Path to Disqus XML export file'
    )
    parser.add_argument(
        '--token', '-t',
        required=True,
        help='GitHub Personal Access Token with repo and write:discussion scopes'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Parse and show what would be migrated without creating discussions'
    )
    
    args = parser.parse_args()
    
    print("Parsing Disqus export...")
    threads = parse_disqus_export(args.export)
    
    print(f"Found {len(threads)} threads with comments")
    
    if args.dry_run:
        print("\n=== DRY RUN MODE ===\n")
        for thread_id, thread in threads.items():
            print(f"Thread: {thread['pathname']}")
            print(f"  URL: {thread['url']}")
            print(f"  Comments: {len(thread['comments'])}")
            for c in thread['comments'][:3]:  # Show first 3 comments
                print(f"    - {c['author']}: {c['message'][:50]}...")
            if len(thread['comments']) > 3:
                print(f"    ... and {len(thread['comments']) - 3} more")
            print()
    
    migrate_threads(threads, args.token, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
