#!/usr/bin/env python3
"""
Simple validation tests for the GitLab to GitHub migrator.
This script validates the basic functionality without making actual API calls.
"""

import json
import sys
import os

# Add parent directory to path to import the migrator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test that config files can be loaded."""
    print("Testing config loading...")
    
    # Test template config
    try:
        with open('config.template.json', 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        assert 'gitlab' in config
        assert 'github' in config
        assert 'url' in config['gitlab']
        assert 'token' in config['gitlab']
        assert 'project_id' in config['gitlab']
        assert 'token' in config['github']
        assert 'owner' in config['github']
        assert 'repo' in config['github']
        
        print("  ✅ Config template is valid")
        return True
    except Exception as e:
        print(f"  ❌ Config validation failed: {e}")
        return False

def test_migrator_class():
    """Test that the migrator class can be instantiated."""
    print("Testing migrator class instantiation...")
    
    try:
        # Import without making requests
        from gitlab_to_github import GitLabToGitHubMigrator
        
        # Create a test config
        config = {
            'gitlab': {
                'url': 'https://gitlab.com',
                'token': 'test-token',
                'project_id': '12345'
            },
            'github': {
                'token': 'test-token',
                'owner': 'test-org',
                'repo': 'test-repo'
            },
            'dry_run': True
        }
        
        # Instantiate migrator
        migrator = GitLabToGitHubMigrator(config)
        
        # Validate attributes
        assert migrator.gitlab_url == 'https://gitlab.com'
        assert migrator.github_owner == 'test-org'
        assert migrator.github_repo == 'test-repo'
        assert migrator.dry_run == True
        
        print("  ✅ Migrator class instantiates correctly")
        return True
    except Exception as e:
        print(f"  ❌ Migrator class test failed: {e}")
        return False

def test_user_mapping():
    """Test user mapping functionality."""
    print("Testing user mapping...")
    
    try:
        from gitlab_to_github import GitLabToGitHubMigrator
        
        config = {
            'gitlab': {'url': 'https://gitlab.com', 'token': 'test', 'project_id': '1'},
            'github': {'token': 'test', 'owner': 'org', 'repo': 'repo'},
            'user_mapping': {
                'gitlab_user1': 'github_user1',
                'gitlab_user2': 'github_user2'
            }
        }
        
        migrator = GitLabToGitHubMigrator(config)
        
        # Test mapped users
        assert migrator.map_user('gitlab_user1') == 'github_user1'
        assert migrator.map_user('gitlab_user2') == 'github_user2'
        
        # Test unmapped user (should return original)
        assert migrator.map_user('unknown_user') == 'unknown_user'
        
        print("  ✅ User mapping works correctly")
        return True
    except Exception as e:
        print(f"  ❌ User mapping test failed: {e}")
        return False

def test_issue_formatting():
    """Test issue body formatting."""
    print("Testing issue body formatting...")
    
    try:
        from gitlab_to_github import GitLabToGitHubMigrator
        
        config = {
            'gitlab': {'url': 'https://gitlab.com', 'token': 'test', 'project_id': '1'},
            'github': {'token': 'test', 'owner': 'org', 'repo': 'repo'},
            'user_mapping': {'gitlab_author': 'github_author'}
        }
        
        migrator = GitLabToGitHubMigrator(config)
        
        # Create a mock MR
        mr = {
            'iid': 123,
            'title': 'Test MR',
            'description': 'Test description',
            'state': 'opened',
            'web_url': 'https://gitlab.com/project/repo/-/merge_requests/123',
            'author': {'username': 'gitlab_author'},
            'created_at': '2024-01-01T10:00:00Z',
            'updated_at': '2024-01-02T15:30:00Z',
            'source_branch': 'feature-branch',
            'target_branch': 'main',
            'labels': ['enhancement']
        }
        
        discussions = [
            {
                'author': {'username': 'gitlab_author'},
                'created_at': '2024-01-01T11:00:00Z',
                'body': 'Test comment'
            }
        ]
        
        # Format issue body
        body = migrator.format_issue_body(mr, discussions)
        
        # Validate content
        assert '[GitLab MR !123]' in body or 'Legacy Merge Request' in body
        assert 'gitlab_author' in body
        assert 'github_author' in body
        assert 'Test description' in body
        assert 'Test comment' in body
        assert 'feature-branch' in body
        assert 'main' in body
        
        print("  ✅ Issue formatting works correctly")
        return True
    except Exception as e:
        print(f"  ❌ Issue formatting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 Running GitLab to GitHub Migrator Validation Tests")
    print("="*60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Config Loading", test_config_loading()))
    results.append(("Migrator Class", test_migrator_class()))
    results.append(("User Mapping", test_user_mapping()))
    results.append(("Issue Formatting", test_issue_formatting()))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
