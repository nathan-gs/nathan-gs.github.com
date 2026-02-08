#!/usr/bin/env python3
"""
Add migrated comments as replies to existing GitHub Discussions.

The original migration put comments in the discussion body. This script
reads the body, parses the comments, and adds them as actual replies
so they show up in giscus.

Usage:
    python add_comments_as_replies.py --token YOUR_GITHUB_TOKEN [--dry-run]
"""

import argparse
import requests
import re
import time

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
REPO_OWNER = "nathan-gs"
REPO_NAME = "nathan-gs.github.com"


def get_discussions_with_migrated_content(token):
    """Fetch discussions that have migrated Disqus comments in the body."""
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
                        comments(first: 1) {
                            totalCount
                        }
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
            # Skip discussions starting with post/ or blog/
            if node['title'].startswith('post/') or node['title'].startswith('blog/'):
                print(f"  Skipping (old format): {node['title']}")
                continue
            
            # Check if body contains migrated comments
            if node['body'] and 'Migrated Comments from Disqus' in node['body']:
                # Only process if no replies yet (avoid duplicates)
                if node['comments']['totalCount'] == 0:
                    discussions.append(node)
                else:
                    print(f"  Skipping (already has {node['comments']['totalCount']} comments): {node['title']}")
        
        page_info = data['data']['repository']['discussions']['pageInfo']
        if page_info['hasNextPage']:
            cursor = page_info['endCursor']
        else:
            break
    
    return discussions


def parse_comments_from_body(body):
    """Parse individual comments from the migrated body content."""
    comments = []
    
    # Split by the comment header pattern: ### 💬 Author
    pattern = r'### 💬 (.+?)\n\*(.+?)\*\n\n> (.+?)(?=\n\n---|\Z)'
    matches = re.findall(pattern, body, re.DOTALL)
    
    for match in matches:
        author = match[0].strip()
        date = match[1].strip()
        message = match[2].strip()
        
        comments.append({
            'author': author,
            'date': date,
            'message': message
        })
    
    return comments


def add_comment_to_discussion(token, discussion_id, body):
    """Add a comment/reply to a discussion."""
    mutation = """
    mutation($discussionId: ID!, $body: String!) {
        addDiscussionComment(input: {
            discussionId: $discussionId,
            body: $body
        }) {
            comment {
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
                "body": body
            }
        },
        headers=headers
    )
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description='Add migrated comments as replies to GitHub Discussions'
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
    
    print("Fetching discussions with migrated content...")
    discussions = get_discussions_with_migrated_content(args.token)
    print(f"Found {len(discussions)} discussions with migrated comments\n")
    
    for d in discussions:
        print(f"Processing #{d['number']}: {d['title']}")
        
        comments = parse_comments_from_body(d['body'])
        print(f"  Found {len(comments)} comments to migrate")
        
        for i, comment in enumerate(comments):
            # Format comment as a reply
            reply_body = f"""**{comment['author']}** wrote on *{comment['date']}*:

> {comment['message']}

---
*Migrated from Disqus*"""
            
            if args.dry_run:
                print(f"    [{i+1}] Would add comment by {comment['author']}")
            else:
                result = add_comment_to_discussion(args.token, d['id'], reply_body)
                
                if 'errors' in result:
                    error_msg = str(result['errors'])
                    print(f"    [{i+1}] ERROR: {error_msg}")
                    
                    # If rate limited, wait longer and retry
                    if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                        print(f"    [{i+1}] Rate limited, waiting 60s and retrying...")
                        time.sleep(60)
                        result = add_comment_to_discussion(args.token, d['id'], reply_body)
                        if 'errors' in result:
                            print(f"    [{i+1}] Retry failed: {result['errors']}")
                        else:
                            print(f"    [{i+1}] Retry succeeded for {comment['author']}")
                else:
                    print(f"    [{i+1}] Added comment by {comment['author']}")
                
                time.sleep(2)  # Rate limiting - increased delay
        
        print()
    
    if args.dry_run:
        print("[DRY RUN] No changes made. Run without --dry-run to apply.")
    else:
        print("Done! Comments have been added as replies.")


if __name__ == '__main__':
    main()
