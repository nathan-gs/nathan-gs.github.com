#!/usr/bin/env python3
"""
Delete GitHub Discussions that start with blog/ or post/.

These are old Disqus threads from a different URL format that are not relevant.

Usage:
    python delete_old_discussions.py --token YOUR_GITHUB_TOKEN [--dry-run]
"""

import argparse
import requests
import time

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
REPO_OWNER = "nathan-gs"
REPO_NAME = "nathan-gs.github.com"


def get_discussions_to_delete(token):
    """Fetch discussions that start with blog/ or post/."""
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
        
        for node in nodes:
            if node['title'].startswith('post/') or node['title'].startswith('blog/'):
                discussions.append(node)
        
        page_info = data['data']['repository']['discussions']['pageInfo']
        if page_info['hasNextPage']:
            cursor = page_info['endCursor']
        else:
            break
    
    return discussions


def delete_discussion(token, discussion_id):
    """Delete a discussion."""
    mutation = """
    mutation($discussionId: ID!) {
        deleteDiscussion(input: {
            id: $discussionId
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
                "discussionId": discussion_id
            }
        },
        headers=headers
    )
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description='Delete GitHub Discussions starting with blog/ or post/'
    )
    parser.add_argument(
        '--token', '-t',
        required=True,
        help='GitHub Personal Access Token'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be deleted without making changes'
    )
    
    args = parser.parse_args()
    
    print("Fetching discussions to delete...")
    discussions = get_discussions_to_delete(args.token)
    print(f"Found {len(discussions)} discussions to delete\n")
    
    if not discussions:
        print("Nothing to delete!")
        return
    
    deleted = 0
    
    for d in discussions:
        print(f"#{d['number']}: {d['title']}")
        
        if args.dry_run:
            print(f"  [DRY RUN] Would delete")
        else:
            result = delete_discussion(args.token, d['id'])
            
            if 'errors' in result:
                error_msg = str(result['errors'])
                print(f"  ERROR: {error_msg}")
                
                if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                    print(f"  Rate limited, waiting 60s...")
                    time.sleep(60)
                    result = delete_discussion(args.token, d['id'])
                    if 'errors' in result:
                        print(f"  Retry failed: {result['errors']}")
                    else:
                        print(f"  ✓ Deleted (after retry)")
                        deleted += 1
            else:
                print(f"  ✓ Deleted")
                deleted += 1
            
            time.sleep(2)  # Rate limiting
    
    print(f"\nDeleted {deleted} discussions")
    
    if args.dry_run:
        print("\n[DRY RUN] No changes made. Run without --dry-run to apply.")


if __name__ == '__main__':
    main()
