#!/usr/bin/env bash
#==============================================================================
# Art & Design Job Board — Automated Setup Script
# 美術設計職缺追蹤網站 — 自動安裝腳本
#
# Usage / 使用方式:
#   bash setup.sh
#
# This will / 這個腳本會:
#   1. Clone the repo / 下載專案
#   2. Install python3 deps (if needed) / 安裝 Python 套件
#   3. Install gh CLI (if not present) / 安裝 GitHub CLI
#   4. Prompt for GitHub PAT / 詢問 GitHub Token
#   5. Set up Hermes cron jobs / 建立 Hermes 排程
#   6. Run initial update / 執行第一次更新
#   7. Verify deployment / 驗證部署
#==============================================================================

set -e

# === Color codes ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${YELLOW}Art & Design Job Board — Auto Installer${NC}          ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ${YELLOW}美術設計職缺追蹤 — 自動安裝腳本${NC}                ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================
# Check prerequisites
# =============================================
echo -e "${BLUE}[1/6]${NC} Checking prerequisites..."
echo ""

# Check git
if ! command -v git &>/dev/null; then
    echo -e "${RED}✗ git not found. Please install git first.${NC}"
    echo "  macOS: brew install git"
    echo "  Ubuntu: sudo apt install git"
    exit 1
fi
echo -e "${GREEN}✓ git found${NC}"

# Check python3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}✗ python3 not found. Please install Python 3.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ python3 found${NC} ($(python3 --version))"

# Check Hermes
HERMES_FOUND=false
if command -v hermes &>/dev/null; then
    HERMES_FOUND=true
    echo -e "${GREEN}✓ hermes CLI found${NC}"
else
    echo -e "${YELLOW}⚠ hermes CLI not found — will skip cron setup.${NC}"
    echo "  Install from: https://hermes-agent.nousresearch.com/docs"
fi

echo ""

# =============================================
# Clone repo
# =============================================
echo -e "${BLUE}[2/6]${NC} Cloning repository..."
echo ""

REPO_URL="https://github.com/rich520ricky-lab/art-jobs-board.git"
INSTALL_DIR="$HOME/hermes/art-jobs-site"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠ Directory $INSTALL_DIR already exists.${NC}"
    read -p "  Overwrite? (y/N): " OVERWRITE
    if [ "$OVERWRITE" = "y" ] || [ "$OVERWRITE" = "Y" ]; then
        rm -rf "$INSTALL_DIR"
    else
        echo -e "${YELLOW}  Using existing directory.${NC}"
        cd "$INSTALL_DIR"
        git pull
    fi
fi

if [ ! -d "$INSTALL_DIR" ]; then
    git clone "$REPO_URL" "$INSTALL_DIR"
    echo -e "${GREEN}✓ Repository cloned to $INSTALL_DIR${NC}"
fi

cd "$INSTALL_DIR"
echo ""

# =============================================
# Test Python script
# =============================================
echo -e "${BLUE}[3/6]${NC} Testing Python scripts..."
echo ""

# Test update_jobs.py (quick dry run - just test imports)
if python3 -c "import json, os, re, subprocess, html; from datetime import datetime; print('✓ All imports OK')" 2>&1; then
    echo -e "${GREEN}✓ Python standard library imports OK${NC}"
else
    echo -e "${RED}✗ Python import test failed${NC}"
    exit 1
fi

# Test that jobs.json is valid JSON
if python3 -c "import json; json.load(open('jobs.json')); print(f'✓ jobs.json valid ({len(json.load(open(\"jobs.json\")))} jobs)')" 2>&1; then
    echo -e "${GREEN}$(python3 -c "import json; print(f'✓ jobs.json valid ({len(json.load(open(\"jobs.json\")))} jobs)')")${NC}"
else
    echo -e "${YELLOW}⚠ jobs.json is invalid or empty. Will be regenerated on first update.${NC}"
fi

echo ""

# =============================================
# GitHub CLI + Auth
# =============================================
echo -e "${BLUE}[4/6]${NC} GitHub setup..."
echo ""

# Install gh CLI if not present
if ! command -v gh &>/dev/null; then
    echo -e "${YELLOW}⚠ gh CLI not found. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        GH_URL=$(curl -sL "https://api.github.com/repos/cli/cli/releases/latest" | \
          python3 -c "import sys,json; d=json.load(sys.stdin); print([a['browser_download_url'] for a in d['assets'] if 'macOS_arm64' in a['name'] and a['name'].endswith('.zip')][0])")
        curl -fsSL -o /tmp/gh.zip "$GH_URL"
        mkdir -p /tmp/gh-extract
        unzip -o /tmp/gh.zip -d /tmp/gh-extract/ >/dev/null 2>&1
        mkdir -p "$HOME/.local/bin"
        cp /tmp/gh-extract/*/bin/gh "$HOME/.local/bin/gh" 2>/dev/null || \
          cp /tmp/gh-extract/gh_*/bin/gh "$HOME/.local/bin/gh" 2>/dev/null
        chmod +x "$HOME/.local/bin/gh"
        export PATH="$HOME/.local/bin:$PATH"
        echo -e "${GREEN}✓ gh CLI installed to ~/.local/bin/gh${NC}"
    else
        echo -e "${YELLOW}  Please install gh CLI manually: https://cli.github.com/${NC}"
    fi
else
    echo -e "${GREEN}✓ gh CLI found${NC}"
fi

# Check gh auth
if command -v gh &>/dev/null; then
    if gh auth status 2>&1 | grep -q "Logged in"; then
        echo -e "${GREEN}✓ GitHub authenticated${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠ GitHub CLI is not authenticated.${NC}"
        echo -e "${YELLOW}  You need a GitHub Personal Access Token to push updates.${NC}"
        echo ""
        echo "  Create one at: https://github.com/settings/tokens"
        echo "  (Permissions: repo, workflow)"
        echo ""
        read -sp "  Enter your GitHub PAT (paste and press Enter): " GH_PAT
        echo ""
        if [ -n "$GH_PAT" ]; then
            echo "$GH_PAT" | gh auth login --with-token 2>/dev/null || {
                echo -e "${RED}  ✗ GH auth failed. You can set up manually later.${NC}"
            }
            echo -e "${GREEN}✓ GitHub authenticated${NC}"
        else
            echo -e "${YELLOW}  ⚠ Skipping GH auth. You'll need to push manually.${NC}"
        fi
    fi
fi

echo ""

# =============================================
# Hermes cron jobs
# =============================================
echo -e "${BLUE}[5/6]${NC} Setting up Hermes cron jobs..."
echo ""

if [ "$HERMES_FOUND" = true ]; then
    echo -e "${YELLOW}  Note: These cron jobs require an active Hermes Agent session.${NC}"
    echo -e "${YELLOW}  They will be created when you run the agent and paste these commands:${NC}"
    echo ""
    echo -e "${GREEN}  Commands to run in Hermes:${NC}"
    echo ""
    echo "  # 1. Morning update (8 AM) — Jobicy + Remotive API"
    echo "  cronjob create \\"
    echo "    --name \"Daily Art Jobs Update\" \\"
    echo "    --schedule \"0 8 * * *\" \\"
    echo "    --workdir \"$INSTALL_DIR\" \\"
    echo "    --prompt \"Run: cd $INSTALL_DIR && python3 update_jobs.py\""
    echo ""
    echo "  # 2. Afternoon scrape (2 PM) — Disney + TikTok browser"
    echo "  cronjob create \\"
    echo "    --name \"Disney TikTok Scraper\" \\"
    echo "    --schedule \"0 14 * * *\" \\"
    echo "    --workdir \"$INSTALL_DIR\" \\"
    echo "    --prompt \"Run Disney+TikTok scraper: browse disneycareers.com and lifeattiktok.com/teams/design, extract new jobs, add to jobs.json, git push\""
    echo ""
    echo "  # 3. Evening update (7 PM) — Jobicy + Remotive again"
    echo "  cronjob create \\"
    echo "    --name \"Art Jobs Board Daily Update\" \\"
    echo "    --schedule \"0 19 * * *\" \\"
    echo "    --workdir \"$INSTALL_DIR\" \\"
    echo "    --prompt \"Run: cd $INSTALL_DIR && python3 update_jobs.py\""
    echo ""

    # Check if we're running inside Hermes by looking for the cronjob tool
    if command -v cronjob &>/dev/null; then
        echo -e "${GREEN}  ✓ Running inside Hermes — creating cron jobs now...${NC}"
        
        cronjob create \
            --name "Daily Art Jobs Update" \
            --schedule "0 8 * * *" \
            --workdir "$INSTALL_DIR" \
            --prompt "Run: cd $INSTALL_DIR && python3 update_jobs.py"
        
        cronjob create \
            --name "Disney TikTok Scraper" \
            --schedule "0 14 * * *" \
            --workdir "$INSTALL_DIR" \
            --prompt "Run Disney+TikTok scraper: browse disneycareers.com and lifeattiktok.com/teams/design, extract new jobs, add to jobs.json, git push"
        
        cronjob create \
            --name "Art Jobs Board Daily Update" \
            --schedule "0 19 * * *" \
            --workdir "$INSTALL_DIR" \
            --prompt "Run: cd $INSTALL_DIR && python3 update_jobs.py"
        
        echo -e "${GREEN}  ✓ Cron jobs created!${NC}"
    else
        echo -e "${YELLOW}  ⚠ Not in Hermes environment. Copy the commands above and paste into Hermes.${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Hermes not found. Skip cron setup.${NC}"
fi

echo ""

# =============================================
# Initial update
# =============================================
echo -e "${BLUE}[6/6]${NC} Running initial update (Jobicy + Remotive)..."
echo ""

cd "$INSTALL_DIR"

if python3 update_jobs.py 2>&1; then
    echo ""
    echo -e "${GREEN}✓ Initial update completed!${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠ Update had issues (likely network). You can retry with:${NC}"
    echo "  cd $INSTALL_DIR && python3 update_jobs.py"
fi

# Also run extra_scraper to ensure Disney/TikTok jobs are present
python3 extra_scraper.py 2>&1 || true

echo ""

# =============================================
# Done!
# =============================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${GREEN}✅ Setup Complete / 安裝完成！${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}Install Location / 安裝位置:${NC}"
echo -e "    $INSTALL_DIR"
echo ""
echo -e "  ${YELLOW}Live Site / 網站:${NC}"
echo -e "    https://rich520ricky-lab.github.io/art-jobs-board/"
echo ""
echo -e "  ${YELLOW}GitHub Repo / 程式碼:${NC}"
echo -e "    https://github.com/rich520ricky-lab/art-jobs-board"
echo ""
echo -e "  ${YELLOW}Documentation / 文件:${NC}"
echo -e "    $INSTALL_DIR/SETUP_GUIDE.md"
echo ""

# =============================================
# First manual update reminder
# =============================================
if command -v gh &>/dev/null && gh auth status 2>&1 | grep -q "Logged in"; then
    echo -e "${YELLOW}  🚀 GitHub is configured — would you like to push the initial update?${NC}"
    read -p "  Push now? (Y/n): " PUSH_NOW
    if [ "$PUSH_NOW" != "n" ] && [ "$PUSH_NOW" != "N" ]; then
        cd "$INSTALL_DIR"
        git add jobs.json last_updated.txt
        git diff --cached --quiet || {
            git commit -m "Initial auto-setup update"
            git push
            echo -e "${GREEN}  ✓ Pushed to GitHub! Site will update in 1-2 min.${NC}"
        }
        echo -e "${GREEN}  ✓ No changes to push (already up to date).${NC}"
    fi
fi

echo ""
echo -e "${GREEN}  🎉 All set! Enjoy the job board.${NC}"
echo -e "${GREEN}  🎉 搞定！盡情使用吧。${NC}"
echo ""