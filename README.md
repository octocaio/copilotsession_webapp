# copilotsession_webapp

A simple vanilla HTML/CSS/JS web application with color-changing functionality.

## Features

- **Change Color**: Click to randomly change the color of the display box
- **Reset**: Reset the box to its original color
- Clean, modern UI with smooth animations

## Setup Instructions

**IMPORTANT: Forking Requirements**

**1. Fork this repository into the `wexinc` organization** (or your EMU organization if you have been migrated).

**2. When forking, you MUST rename the repository to start with `fork_copilotsession...`**
   - Example: `fork_copilotsession_yourname`
   - Example: `fork_copilotsession_team1`
   - **This naming convention is required for automated cleanup scripts.**

## Running the Application

1. Clone your forked repository
2. Open `index.html` in your web browser
3. Click the "Change Color" button to change the box color
4. Click the "Reset" button to return to the default color

No build process or dependencies required - just open `index.html` in any modern web browser!

## Files

- `index.html` - Main HTML structure
- `style.css` - Styling and layout
- `app.js` - JavaScript functionality for color changes

## 🔧 Additional Tools

### GitHub Actions Storage Guide

Comprehensive guide explaining GitHub Actions storage usage, billing, and optimization strategies.

**Documentation:** [GitHub Actions Storage Guide](GITHUB_ACTIONS_ARMAZENAMENTO.md) (Portuguese)

**Topics covered:**
- 📊 How artifacts and cache consume storage quota
- 💰 Understanding billing and cost calculation
- 🔍 Methods to check actual storage consumption
- ⚡ Practical strategies to reduce storage usage
- 🤖 Automated cleanup scripts and workflows

### GitLab to GitHub MR Migrator

This repository includes a comprehensive tool for migrating GitLab Merge Requests to GitHub Issues for historical and audit purposes.

**Location:** `/migrator`

**Documentation:**
- [Complete Migration Guide](migrator/README.md) - Detailed documentation in Portuguese
- [Quick Start Guide](migrator/QUICK_START.md) - Get started in 5 minutes

**Features:**
- ✅ Migrate GitLab MRs to GitHub Issues
- ✅ Preserve complete history, comments, and metadata
- ✅ User mapping (GitLab → GitHub)
- ✅ Automated labeling and categorization
- ✅ Dry-run mode for testing
- ✅ Interactive migration script

**Quick Usage:**
```bash
cd migrator
pip install -r requirements.txt
cp config.template.json config.json
# Edit config.json with your credentials
python3 gitlab_to_github.py --config config.json --dry-run
```

See the [migrator documentation](migrator/README.md) for complete details.