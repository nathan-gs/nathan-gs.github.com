#!/usr/bin/env python3
"""
Fix GitHub Discussion titles by removing leading slashes.

This script updates discussion titles that start with '/' to match giscus pathname mapping.

Usage:
    python fix_discussion_titles.py --token YOUR_GITHUB_TOKEN [--dry-run]
"""

import argparse
import requests
import time

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
REPO_OWNER = "nathan-gs"
REPO_NAME = "nathan-gs.github.com"


def get_discussions(token):
    """Fetch all discussions from the repository."""
    discussions = []
    cursor = None
    
    while True:
        query = """
        query($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                discussions(first: 100, after: $cursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        title
                        number
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


def update_discussion_title(token, discussion_id, new_title):
    """Update a discussion's title."""
    mutation = """
    mutation($discussionId: ID!, $title: String!) {
        updateDiscussion(input: {
            discussionId: $discussionId,
            title: $title
        }) {
            discussion {
                id
                title
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
                "title": new_title
            }
        },
        headers=headers
    )
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description='Fix GitHub Discussion titles by removing leading slashes'
    )
    parser.add_argument(
        '--token', '-t',
        required=True,
        help='GitHub Personal Access Token'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    
    args = parser.parse_args()
    
    print("Fetching discussions...")
    discussions = get_discussions(args.token)
    print(f"Found {len(discussions)} discussions\n")
    
    # Find discussions with leading slash
    to_fix = []
    for d in discussions:
        if d['title'].startswith('/'):
            to_fix.append(d)
    
    if not to_fix:
        print("No discussions need fixing!")
        return
    
    print(f"Found {len(to_fix)} discussions with leading slash:\n")
    
    for d in to_fix:
        old_title = d['title']
        new_title = old_title.lstrip('/')
        
        print(f"#{d['number']}: {old_title}")
        print(f"     → {new_title}")
        
        if not args.dry_run:
            result = update_discussion_title(args.token, d['id'], new_title)
            
            if 'errors' in result:
                print(f"     ERROR: {result['errors']}")
            else:
                print(f"     ✓ Updated")
            
            time.sleep(0.5)  # Rate limiting
        
        print()
    
    if args.dry_run:
        print("\n[DRY RUN] No changes made. Run without --dry-run to apply changes.")
    else:
        print("\nDone!")


if __name__ == '__main__':
    main()
