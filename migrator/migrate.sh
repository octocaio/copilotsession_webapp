#!/bin/bash
# Example usage script for GitLab to GitHub MR migration

echo "🚀 GitLab to GitHub MR Migration - Example Usage"
echo "================================================"
echo ""

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "⚠️  config.json not found. Creating from template..."
    cp config.template.json config.json
    echo "✅ Created config.json - Please edit it with your credentials"
    echo ""
    echo "Required fields:"
    echo "  - gitlab.token: Your GitLab Personal Access Token"
    echo "  - gitlab.project_id: Your GitLab Project ID"
    echo "  - github.token: Your GitHub Personal Access Token"
    echo "  - github.owner: Your GitHub organization or username"
    echo "  - github.repo: Your GitHub repository name"
    echo ""
    exit 1
fi

# Check if Python dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
else
    echo "✅ Dependencies OK"
fi

echo ""
echo "Choose migration mode:"
echo "1) Dry run - Test migration (no changes made)"
echo "2) Migrate first 5 MRs only (test)"
echo "3) Migrate all opened MRs"
echo "4) Migrate all MRs (opened, closed, merged)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🔍 Running DRY RUN..."
        python3 gitlab_to_github.py --config config.json --dry-run
        ;;
    2)
        echo ""
        echo "🔍 Migrating first 5 MRs (test)..."
        python3 gitlab_to_github.py --config config.json --max 5
        ;;
    3)
        echo ""
        echo "⚠️  This will migrate ALL opened MRs from GitLab to GitHub."
        read -p "Continue? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            echo "🚀 Starting migration..."
            python3 gitlab_to_github.py --config config.json --state opened
        else
            echo "❌ Cancelled"
        fi
        ;;
    4)
        echo ""
        echo "⚠️  This will migrate ALL MRs (opened, closed, merged) from GitLab to GitHub."
        read -p "Continue? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            echo "🚀 Starting migration..."
            python3 gitlab_to_github.py --config config.json --state all
        else
            echo "❌ Cancelled"
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done! Check your GitHub repository for migrated issues."
