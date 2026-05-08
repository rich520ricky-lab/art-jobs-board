#!/usr/bin/env bash
#==============================================================================
# Art & Design Job Board — Hermes Memory & Config Backup Script
# 美術設計職缺追蹤 — Hermes 記憶與設定備份腳本
#
# This script backs up your Hermes memories, config, and cron jobs into
# the GitHub repo, so they can be restored on a new computer.
#
# 這個腳本會把 Hermes 的記憶、設定、排程任務備份到 GitHub repo 中，
# 讓新電腦可以透過 setup.sh 一鍵還原。
#
# Usage / 使用方式:
#   bash backup.sh
#
# What gets backed up / 備份內容:
#   - ~/.hermes/memories/MEMORY.md    → .hermes-backup/memory.md
#   - ~/.hermes/memories/USER.md      → .hermes-backup/user.md
#   - ~/.hermes/config.yaml           → .hermes-backup/config.yaml
#   - ~/.hermes/mlx-model-config.yaml → .hermes-backup/mlx-model-config.yaml
#   - ~/.hermes/cron/jobs.json        → .hermes-backup/cron-jobs.json
#
# What does NOT get backed up (for security / 不會備份):
#   - .env file (API keys / API 金鑰)
#   - state.db (session data / 對話記錄)
#   - channel_directory.json (channel tokens)
#   - auth.json (auth tokens)
#==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$REPO_DIR/.hermes-backup"
HERMES_DIR="$HOME/.hermes"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${YELLOW}Hermes Memory & Config Backup${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ${YELLOW}Hermes 記憶與設定備份${NC}                          ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================
# Create backup directory
# =============================================
mkdir -p "$BACKUP_DIR"
echo -e "${BLUE}[1/5]${NC} Backup directory: $BACKUP_DIR"
echo ""

# =============================================
# Backup memories
# =============================================
echo -e "${BLUE}[2/5]${NC} Backing up Hermes memories..."
echo ""

if [ -f "$HERMES_DIR/memories/MEMORY.md" ]; then
    cp "$HERMES_DIR/memories/MEMORY.md" "$BACKUP_DIR/memory.md"
    echo -e "  ${GREEN}✓${NC} MEMORY.md ($(wc -c < "$HERMES_DIR/memories/MEMORY.md") bytes)"
else
    echo -e "  ${YELLOW}⚠${NC} MEMORY.md not found — skipping"
    echo "MEMORY.md not found" > "$BACKUP_DIR/memory.md"
fi

if [ -f "$HERMES_DIR/memories/USER.md" ]; then
    cp "$HERMES_DIR/memories/USER.md" "$BACKUP_DIR/user.md"
    echo -e "  ${GREEN}✓${NC} USER.md ($(wc -c < "$HERMES_DIR/memories/USER.md") bytes)"
else
    echo -e "  ${YELLOW}⚠${NC} USER.md not found — skipping"
    echo "USER.md not found" > "$BACKUP_DIR/user.md"
fi

echo ""

# =============================================
# Backup config
# =============================================
echo -e "${BLUE}[3/5]${NC} Backing up Hermes configuration..."
echo ""

if [ -f "$HERMES_DIR/config.yaml" ]; then
    # Redact secrets before copying
    python3 -c "
import re
with open('$HERMES_DIR/config.yaml') as f:
    content = f.read()
for pattern, replacement in [
    (r'(api_key:\s*).*', r'\1\"REDACTED_BACKUP_see_original_env\"'),
    (r'(client_secret:\s*).*', r'\1\"REDACTED_BACKUP_see_original_env\"'),
    (r'(client_id:\s*).*', r'\1\"REDACTED_BACKUP_see_original_env\"'),
    (r'(access_token:\s*).*', r'\1\"REDACTED_BACKUP_see_original_env\"'),
    (r'(password:\s*).*', r'\1\"REDACTED_BACKUP_see_original_env\"'),
]:
    content = re.sub(pattern, replacement, content)
with open('$BACKUP_DIR/config.yaml', 'w') as f:
    f.write(content)
"
    echo -e "  ${GREEN}✓${NC} config.yaml ($(wc -c < "$HERMES_DIR/config.yaml") bytes, secrets redacted)"
else
    echo -e "  ${YELLOW}⚠${NC} config.yaml not found — skipping"
fi

if [ -f "$HERMES_DIR/mlx-model-config.yaml" ]; then
    cp "$HERMES_DIR/mlx-model-config.yaml" "$BACKUP_DIR/mlx-model-config.yaml"
    echo -e "  ${GREEN}✓${NC} mlx-model-config.yaml ($(wc -c < "$HERMES_DIR/mlx-model-config.yaml") bytes)"
else
    echo -e "  ${YELLOW}⚠${NC} mlx-model-config.yaml not found — skipping"
fi

echo ""

# =============================================
# Backup cron jobs
# =============================================
echo -e "${BLUE}[4/5]${NC} Backing up Hermes cron jobs..."
echo ""

if [ -f "$HERMES_DIR/cron/jobs.json" ]; then
    cp "$HERMES_DIR/cron/jobs.json" "$BACKUP_DIR/cron-jobs.json"
    echo -e "  ${GREEN}✓${NC} cron/jobs.json ($(wc -c < "$HERMES_DIR/cron/jobs.json") bytes)"
    
    # Show summary of what's backed up
    echo ""
    echo -e "  ${YELLOW}Cron jobs backed up:${NC}"
    python3 -c "
import json
with open('$BACKUP_DIR/cron-jobs.json') as f:
    data = json.load(f)
for j in data.get('jobs', []):
    name = j.get('name', 'Unnamed')
    sched = j.get('schedule', {}).get('display', '?')
    enabled = '✅' if j.get('enabled', False) else '⏸️'
    print(f'    {enabled} {name:35s} | {sched}')
print(f'    ---')
print(f'    Total: {len(data.get(\"jobs\", []))} jobs')
"
else
    echo -e "  ${YELLOW}⚠${NC} cron/jobs.json not found — skipping"
fi

echo ""

# =============================================
# Git commit & push
# =============================================
echo -e "${BLUE}[5/5]${NC} Committing and pushing to GitHub..."
echo ""

cd "$REPO_DIR"

git add .hermes-backup/

# Check if there are changes
if git diff --cached --quiet; then
    echo -e "  ${YELLOW}⚠ No changes since last backup.${NC}"
else
    # Create a summary of what changed
    BACKUP_DATE=$(date "+%Y-%m-%d %H:%M")
    git commit -m "Hermes backup: $BACKUP_DATE"
    
    if git push 2>&1; then
        echo -e "  ${GREEN}✓ Backup pushed to GitHub!${NC}"
    else
        echo -e "  ${RED}✗ Push failed. Check your git remote and auth.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}  ✅ Backup complete! / 備份完成！${NC}"
echo ""
echo -e "  ${YELLOW}Backed up to / 備份位置:${NC}"
echo -e "    $BACKUP_DIR/"
echo -e "    https://github.com/rich520ricky-lab/art-jobs-board/tree/main/.hermes-backup"
echo ""
echo -e "  ${YELLOW}To restore on new computer / 在新電腦還原:${NC}"
echo -e "    bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/rich520ricky-lab/art-jobs-board/main/setup.sh)\""
echo ""