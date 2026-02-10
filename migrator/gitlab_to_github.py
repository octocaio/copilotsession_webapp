#!/usr/bin/env python3
"""
GitLab to GitHub MR Migrator

This script migrates GitLab Merge Requests to GitHub Issues for historical
and audit purposes. It does NOT migrate pipeline associations or active workflows.

Usage:
    python gitlab_to_github.py --config config.json
"""

import argparse
import json
import sys
import time
from typing import Dict, List, Optional
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests library not found. Please install: pip install requests")
    sys.exit(1)


class GitLabToGitHubMigrator:
    """Migrates GitLab Merge Requests to GitHub Issues for audit/historical purposes."""
    
    def __init__(self, config: Dict):
        """
        Initialize the migrator with configuration.
        
        Args:
            config: Dictionary containing GitLab and GitHub credentials and repo info
        """
        self.config = config
        self.gitlab_url = config['gitlab']['url']
        self.gitlab_token = config['gitlab']['token']
        self.gitlab_project_id = config['gitlab']['project_id']
        
        self.github_url = config['github'].get('api_url', 'https://api.github.com')
        self.github_token = config['github']['token']
        self.github_owner = config['github']['owner']
        self.github_repo = config['github']['repo']
        
        self.user_mapping = config.get('user_mapping', {})
        self.dry_run = config.get('dry_run', False)
        self.rate_limit_delay = config.get('rate_limit_delay', 1)
        
        # Statistics
        self.stats = {
            'total_mrs': 0,
            'migrated': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def get_gitlab_headers(self) -> Dict[str, str]:
        """Get headers for GitLab API requests."""
        return {
            'PRIVATE-TOKEN': self.gitlab_token,
            'Content-Type': 'application/json'
        }
    
    def get_github_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        return {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
    
    def fetch_gitlab_merge_requests(self, state: str = 'opened') -> List[Dict]:
        """
        Fetch merge requests from GitLab.
        
        Args:
            state: State of MRs to fetch (opened, closed, merged, all)
            
        Returns:
            List of merge request objects
        """
        print(f"\n📥 Fetching {state} merge requests from GitLab...")
        
        url = f"{self.gitlab_url}/api/v4/projects/{self.gitlab_project_id}/merge_requests"
        params = {
            'state': state,
            'per_page': 100,
            'order_by': 'updated_at',
            'sort': 'desc'
        }
        
        all_mrs = []
        page = 1
        
        while True:
            params['page'] = page
            try:
                response = requests.get(url, headers=self.get_gitlab_headers(), params=params)
                response.raise_for_status()
                
                mrs = response.json()
                if not mrs:
                    break
                
                all_mrs.extend(mrs)
                print(f"  Fetched page {page} ({len(mrs)} MRs)")
                page += 1
                
                # Check if there are more pages
                if 'x-next-page' not in response.headers or not response.headers['x-next-page']:
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Error fetching MRs from GitLab: {e}")
                break
        
        print(f"✅ Total MRs fetched: {len(all_mrs)}")
        self.stats['total_mrs'] = len(all_mrs)
        return all_mrs
    
    def fetch_mr_discussions(self, mr_iid: int) -> List[Dict]:
        """
        Fetch all discussions/comments for a merge request.
        
        Args:
            mr_iid: Internal ID of the merge request
            
        Returns:
            List of discussion objects
        """
        url = f"{self.gitlab_url}/api/v4/projects/{self.gitlab_project_id}/merge_requests/{mr_iid}/notes"
        
        try:
            response = requests.get(url, headers=self.get_gitlab_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Warning: Could not fetch discussions for MR !{mr_iid}: {e}")
            return []
    
    def map_user(self, gitlab_username: str) -> str:
        """
        Map GitLab username to GitHub username.
        
        Args:
            gitlab_username: GitLab username
            
        Returns:
            GitHub username or original if no mapping exists
        """
        return self.user_mapping.get(gitlab_username, gitlab_username)
    
    def format_issue_body(self, mr: Dict, discussions: List[Dict]) -> str:
        """
        Format the GitHub issue body with MR information.
        
        Args:
            mr: GitLab merge request object
            discussions: List of discussion/comment objects
            
        Returns:
            Formatted markdown string for GitHub issue body
        """
        author = mr['author']['username']
        github_author = self.map_user(author)
        
        # Build the issue body
        body_parts = [
            "## 📋 Legacy Merge Request (GitLab)",
            "",
            f"**Original MR:** {mr['web_url']}",
            f"**Author:** @{github_author} (GitLab: @{author})",
            f"**Status at migration:** {mr['state']}",
            f"**Created:** {mr['created_at']}",
            f"**Last updated:** {mr['updated_at']}",
        ]
        
        # Add merge status if merged
        if mr['state'] == 'merged' and mr.get('merged_at'):
            body_parts.append(f"**Merged at:** {mr['merged_at']}")
            if mr.get('merged_by'):
                merged_by = mr['merged_by']['username']
                body_parts.append(f"**Merged by:** @{self.map_user(merged_by)} (GitLab: @{merged_by})")
        
        # Add source and target branches
        body_parts.extend([
            f"**Source branch:** `{mr['source_branch']}`",
            f"**Target branch:** `{mr['target_branch']}`",
            ""
        ])
        
        # Add labels if present
        if mr.get('labels'):
            labels_str = ", ".join([f"`{label}`" for label in mr['labels']])
            body_parts.extend([
                f"**Original labels:** {labels_str}",
                ""
            ])
        
        # Add description
        body_parts.extend([
            "### Description",
            "",
            mr.get('description', '_No description provided_'),
            ""
        ])
        
        # Add discussions/comments
        if discussions:
            body_parts.extend([
                "### Discussion History",
                "",
                f"_This MR had {len(discussions)} comment(s) in GitLab:_",
                ""
            ])
            
            for note in discussions:
                comment_author = note['author']['username']
                github_comment_author = self.map_user(comment_author)
                created_at = note['created_at']
                
                body_parts.extend([
                    f"**@{github_comment_author}** (GitLab: @{comment_author}) - {created_at}",
                    f"> {note['body']}",
                    ""
                ])
        
        # Add footer
        body_parts.extend([
            "---",
            "",
            "_This issue was automatically created for historical and audit purposes._",
            "_The original merge request remains available in GitLab for reference._"
        ])
        
        return "\n".join(body_parts)
    
    def create_github_issue(self, mr: Dict) -> Optional[Dict]:
        """
        Create a GitHub issue from a GitLab merge request.
        
        Args:
            mr: GitLab merge request object
            
        Returns:
            Created GitHub issue object or None if failed
        """
        mr_iid = mr['iid']
        mr_title = mr['title']
        
        print(f"\n📝 Processing MR !{mr_iid}: {mr_title}")
        
        if self.dry_run:
            print("  🔍 DRY RUN: Would create GitHub issue")
            self.stats['migrated'] += 1
            return {'dry_run': True}
        
        # Fetch discussions
        discussions = self.fetch_mr_discussions(mr_iid)
        
        # Format issue body
        issue_body = self.format_issue_body(mr, discussions)
        
        # Prepare issue title
        issue_title = f"[GitLab MR !{mr_iid}] {mr_title}"
        
        # Prepare labels
        labels = ['legacy-mr', 'from-gitlab']
        if mr['state'] == 'opened':
            labels.append('was-open')
        elif mr['state'] == 'merged':
            labels.append('was-merged')
        elif mr['state'] == 'closed':
            labels.append('was-closed')
        
        # Create the issue
        url = f"{self.github_url}/repos/{self.github_owner}/{self.github_repo}/issues"
        payload = {
            'title': issue_title,
            'body': issue_body,
            'labels': labels
        }
        
        try:
            response = requests.post(url, headers=self.get_github_headers(), json=payload)
            response.raise_for_status()
            
            issue = response.json()
            print(f"  ✅ Created GitHub issue #{issue['number']}")
            self.stats['migrated'] += 1
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return issue
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Failed to create issue: {e}")
            if hasattr(e.response, 'text'):
                print(f"     Response: {e.response.text}")
            self.stats['failed'] += 1
            return None
    
    def migrate(self, mr_state: str = 'opened', max_mrs: Optional[int] = None):
        """
        Perform the migration.
        
        Args:
            mr_state: State of MRs to migrate (opened, closed, merged, all)
            max_mrs: Maximum number of MRs to migrate (for testing)
        """
        print("\n" + "="*60)
        print("🚀 GitLab to GitHub MR Migration")
        print("="*60)
        print(f"\nSource: GitLab project {self.gitlab_project_id}")
        print(f"Target: GitHub {self.github_owner}/{self.github_repo}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print(f"MR State: {mr_state}")
        
        # Fetch MRs from GitLab
        mrs = self.fetch_gitlab_merge_requests(state=mr_state)
        
        if not mrs:
            print("\n⚠️  No merge requests found to migrate.")
            return
        
        # Limit number of MRs if specified
        if max_mrs:
            mrs = mrs[:max_mrs]
            print(f"\n⚠️  Limiting migration to first {max_mrs} MRs")
        
        # Migrate each MR
        print(f"\n📦 Starting migration of {len(mrs)} merge request(s)...")
        
        for i, mr in enumerate(mrs, 1):
            print(f"\n[{i}/{len(mrs)}]", end=" ")
            self.create_github_issue(mr)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 Migration Summary")
        print("="*60)
        print(f"Total MRs processed: {self.stats['total_mrs']}")
        print(f"Successfully migrated: {self.stats['migrated']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Skipped: {self.stats['skipped']}")
        print("="*60 + "\n")


def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Config file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Migrate GitLab Merge Requests to GitHub Issues for audit/historical purposes'
    )
    parser.add_argument(
        '--config',
        required=True,
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '--state',
        default='opened',
        choices=['opened', 'closed', 'merged', 'all'],
        help='State of MRs to migrate (default: opened)'
    )
    parser.add_argument(
        '--max',
        type=int,
        help='Maximum number of MRs to migrate (for testing)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without actually creating issues'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override dry_run if specified in command line
    if args.dry_run:
        config['dry_run'] = True
    
    # Create migrator and run
    migrator = GitLabToGitHubMigrator(config)
    migrator.migrate(mr_state=args.state, max_mrs=args.max)


if __name__ == '__main__':
    main()
