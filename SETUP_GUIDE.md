# Art & Design Job Board — Setup & Maintenance Guide
# 美術設計職缺追蹤網站 — 安裝與維護手冊

> **GitHub:** https://github.com/rich520ricky-lab/art-jobs-board
> **Live Site:** https://rich520ricky-lab.github.io/art-jobs-board/

---

## EN / English

### Overview

This is a **bilingual (EN/ZH) static job board** that aggregates art & design job openings from multiple sources:
- **Jobicy API** (free, no key needed) — 28+ design/creative jobs
- **Remotive API** (free, no key needed) — 20+ remote design jobs
- **Disney Careers** (browser-scraped) — animation/art roles at Walt Disney Animation Studios, Disney Experiences, Marvel
- **TikTok Careers** (browser-scraped) — Design team roles (Product Designer, Content Designer, etc.)

The site auto-updates daily via **Hermes Agent cron jobs**, and all data is stored as a static `jobs.json` deployed to GitHub Pages.

---

### File Structure

```
art-jobs-site/
├── index.html            # Bilingual job board (EN + ZH toggle)
├── jobs.json             # All job data (add/remove jobs here)
├── last_updated.txt      # Last update date string
├── update_jobs.py        # Daily auto-updater: Jobicy + Remotive + company classification
├── extra_scraper.py      # Browser-based Disney + TikTok scraper (stores known jobs + merge logic)
├── SETUP_GUIDE.md        # This file
└── README.md             # GitHub project description
```

### Jobs JSON Format

Each job entry follows this structure:

```json
{
  "en": {
    "title": "Senior Technical Artist",
    "company": "Riot Games",
    "desc": "Join the animation team..."
  },
  "zh": {
    "title": "資深技術美術師",
    "company": "Riot Games",
    "desc": "加入動畫團隊..."
  },
  "location": "Los Angeles, CA",
  "type": "On-site",
  "category": "Game Art",
  "company_class": "enterprise",
  "salary": "$120K-$180K/yr",
  "posted": "2 days ago",
  "link": "https://...",
  "featured": true,
  "new": true
}
```

**company_class values:** `enterprise` | `mid-small` | `school` | `freelance`

---

### Step 1: Clone & Deploy (New Computer)

```bash
# 1. Clone the repo
git clone https://github.com/rich520ricky-lab/art-jobs-board.git
cd art-jobs-board

# 2. Enable GitHub Pages
# Go to: GitHub repo → Settings → Pages → Deploy from main branch / (root)
# Site will be at: https://rich520ricky-lab.github.io/art-jobs-board/

# 3. (Optional) Install Hermes Agent for cron automation
# See: https://hermes-agent.nousresearch.com/docs
```

---

### Step 2: Manual Update (Any Time)

```bash
cd ~/hermes/art-jobs-site   # or wherever you cloned it

# Run the API scraper (Jobicy + Remotive)
python3 update_jobs.py

# Run the Disney+TikTok known jobs adder (adds stored jobs if new)
python3 extra_scraper.py

# Deploy
git add jobs.json last_updated.txt
git commit -m "Update jobs"
git push
```

---

### Step 3: How to Add Jobs Manually

#### A) Add a single job (quickest)

Open `jobs.json`, copy an existing entry, and edit the fields. Make sure `link` points to the real job URL.

#### B) Scrape Disney Careers (using Hermes Agent browser)

Tell the Hermes agent: "Run Disney career scraper"

The agent will:
1. Go to `https://www.disneycareers.com/en/search-jobs/?q=artist+designer+animator+creative`
2. Extract all job links with this JS in browser console:
   ```javascript
   Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => ({
     title: a.querySelector('h2')?.textContent?.trim(),
     href: a.href
   }))
   ```
3. Add any new jobs to `jobs.json`

#### C) Scrape TikTok Careers

Tell the Hermes agent: "Run TikTok career scraper"

1. Go to `https://lifeattiktok.com/teams/design`
2. Wait for the "Explore open roles in Design" section to load
3. Extract all job listings (links with `/search/` + job ID)
4. Add any new jobs to `jobs.json`

---

### Step 4: Setting Up Automated Cron Jobs (Hermes Agent)

If you're using Hermes Agent, run these commands once to set up daily auto-updates:

```bash
# Morning update (8:00 AM) - Jobicy + Remotive API
cronjob create \
  --name "Daily Art Jobs Update" \
  --schedule "0 8 * * *" \
  --workdir /path/to/art-jobs-site \
  --prompt "Run: cd ~/hermes/art-jobs-site && python3 update_jobs.py"

# Afternoon scrape (2:00 PM) - Disney + TikTok browser scrape
cronjob create \
  --name "Disney TikTok Scraper" \
  --schedule "0 14 * * *" \
  --workdir /path/to/art-jobs-site \
  --prompt "Run Disney+TikTok browser scraper: browse disneycareers.com and lifeattiktok.com/teams/design, extract new jobs, add to jobs.json, git commit+push."

# Evening update (7:00 PM) - Jobicy + Remotive again
cronjob create \
  --name "Art Jobs Board Daily Update" \
  --schedule "0 19 * * *" \
  --workdir /path/to/art-jobs-site \
  --prompt "Run: cd ~/hermes/art-jobs-site && python3 update_jobs.py"
```

To see active jobs:
```bash
cronjob list
```

---

### How Job Sources Work

| Source | Method | Requires | Update Freq |
|--------|--------|----------|-------------|
| **Jobicy API** | HTTP GET to `jobicy.com/api/v2/remote-jobs?tag=design` | Nothing (free) | Every cron run |
| **Remotive API** | HTTP GET to `remotive.com/api/remote-jobs?category=design` | Nothing (free) | Every cron run |
| **Disney Careers** | Browser navigation to disneycareers.com | Hermes browser tool | Daily 2 PM |
| **TikTok Careers** | Browser navigation to lifeattiktok.com/teams/design | Hermes browser tool | Daily 2 PM |
| **Manual** | Add entries directly to jobs.json | Nothing | Anytime |

### Company Classification

The `company_class` field is auto-set by `classify_company()` in `update_jobs.py`:
- **enterprise** — Known big companies (Reddit, Stripe, Disney, Figma, TikTok, etc.)
- **mid-small** — Default for unknown companies
- **school** — Universities, colleges, institutes
- **freelance** — Staffing agencies, freelance platforms (Lemon.io, IAPWE, A.Team, etc.)

To add a new company to a category, edit `BIG_COMPANIES` list or the freelancers list in `update_jobs.py`.

### Bilingual Content

- The site has **EN / 中文** toggle button in the header
- Each job has both `en` and `zh` fields
- If `zh.desc` is empty, the card shows English only
- UI text (filter labels, stats, buttons) is bilingual via `<span class="en-text">` / `<span class="zh-text">` in `index.html`

---

### Troubleshooting

**Q: Site not updating after push?**
- GitHub Pages takes 1-3 minutes to deploy
- Check: `https://github.com/rich520ricky-lab/art-jobs-board/actions`

**Q: Jobs look wrong or duplicated?**
- Delete `jobs.json` and re-run `update_jobs.py` (fetches fresh data)
- Then run `extra_scraper.py` to restore Disney/TikTok jobs

**Q: TikTok scraping not finding jobs?**
- TikTok's career site changes frequently
- Try navigating manually to `https://lifeattiktok.com/teams/design`
- If the page layout changed, the agent may need updated instructions

**Q: Need to move to a new computer?**
1. `git clone` the repo on the new machine
2. Install Hermes Agent
3. Re-create cron jobs with `cronjob create` (see Step 4)
4. Verify: `python3 update_jobs.py` runs without errors

---

---

## ZH / 中文

### 概述

這是一個**中英雙語靜態求職網站**，彙整美術與設計相關職缺，資料來源包括：

- **Jobicy API**（免費，免金鑰）— 28+ 筆設計/創意職缺
- **Remotive API**（免費，免金鑰）— 20+ 筆遠端設計職缺
- **Disney Careers**（瀏覽器爬蟲）— Walt Disney Animation Studios、Disney Experiences、Marvel 的動畫/美術職缺
- **TikTok Careers**（瀏覽器爬蟲）— Design 團隊（Product Designer、Content Designer 等）

網站每天透過 **Hermes Agent 定時任務**自動更新，所有資料以靜態 `jobs.json` 儲存並部署到 GitHub Pages。

---

### 資料夾結構

```
art-jobs-site/
├── index.html            # 中英雙語求職看板（可切換 EN / 中文）
├── jobs.json             # 所有職缺資料（手動增刪也在這裡）
├── last_updated.txt      # 最後更新日期字串
├── update_jobs.py        # 每日自動更新：Jobicy + Remotive + 公司分類
├── extra_scraper.py      # Disney + TikTok 爬蟲輔助腳本（儲存已知職缺 + 合併邏輯）
├── SETUP_GUIDE.md        # 本檔案
└── README.md             # GitHub 專案說明
```

---

### 第一步：克隆與部署（新電腦）

```bash
# 1. 下載專案
git clone https://github.com/rich520ricky-lab/art-jobs-board.git
cd art-jobs-board

# 2. 啟用 GitHub Pages
# 到 GitHub 專頁 → Settings → Pages → Deploy from main branch / (root)
# 網站會出現在：https://rich520ricky-lab.github.io/art-jobs-board/

# 3.（選用）安裝 Hermes Agent 來自動排程
# 官網：https://hermes-agent.nousresearch.com/docs
```

---

### 第二步：手動更新（隨時可做）

```bash
cd ~/hermes/art-jobs-site   # 或你 clone 的位置

# 跑 API 爬蟲（Jobicy + Remotive）
python3 update_jobs.py

# 跑 Disney+TikTok 已知職缺加入腳本
python3 extra_scraper.py

# 部署
git add jobs.json last_updated.txt
git commit -m "更新職缺"
git push
```

---

### 第三步：如何手動新增職缺

#### A) 直接編輯 jobs.json（最快）

打開 `jobs.json`，複製一個現有職缺並修改欄位。確保 `link` 指向真實職缺網址。

#### B) 從 Disney Careers 抓取

告訴 Hermes agent：「去 Disney Careers 抓職缺」

agent 會：
1. 前往 `https://www.disneycareers.com/en/search-jobs/?q=artist+designer+animator+creative`
2. 在瀏覽器 Console 執行以下 JS 提取所有職缺連結：
   ```javascript
   Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => ({
     title: a.querySelector('h2')?.textContent?.trim(),
     href: a.href
   }))
   ```
3. 將新職缺加入 `jobs.json`

#### C) 從 TikTok Careers 抓取

告訴 Hermes agent：「去 TikTok Design 團隊頁面抓職缺」

1. 前往 `https://lifeattiktok.com/teams/design`
2. 等待「Explore open roles in Design」區塊載入
3. 提取所有職缺列表（連結格式為 `/search/` + 職缺 ID）
4. 將新職缺加入 `jobs.json`

---

### 第四步：設定每日自動排程（Hermes Agent）

如果你使用 Hermes Agent，執行以下指令一次即可設定每日自動更新：

```bash
# 早上 8 點 — Jobicy + Remotive API
cronjob create \
  --name "Daily Art Jobs Update" \
  --schedule "0 8 * * *" \
  --workdir /Users/test/hermes/art-jobs-site \
  --prompt "Run: cd ~/hermes/art-jobs-site && python3 update_jobs.py"

# 下午 2 點 — Disney + TikTok 瀏覽器爬蟲
cronjob create \
  --name "Disney TikTok Scraper" \
  --schedule "0 14 * * *" \
  --workdir /Users/test/hermes/art-jobs-site \
  --prompt "Run Disney+TikTok browser scraper: browse disneycareers.com and lifeattiktok.com/teams/design, extract new jobs, add to jobs.json, git commit+push."

# 晚上 7 點 — Jobicy + Remotive 第二次更新
cronjob create \
  --name "Art Jobs Board Daily Update" \
  --schedule "0 19 * * *" \
  --workdir /Users/test/hermes/art-jobs-site \
  --prompt "Run: cd ~/hermes/art-jobs-site && python3 update_jobs.py"
```

查看已設定的排程：
```bash
cronjob list
```

---

### 各資料來源說明

| 來源 | 方式 | 需要 | 更新頻率 |
|------|------|------|----------|
| **Jobicy API** | HTTP GET 到 `jobicy.com/api/v2/remote-jobs?tag=design` | 免費，免金鑰 | 每次 cron 執行 |
| **Remotive API** | HTTP GET 到 `remotive.com/api/remote-jobs?category=design` | 免費，免金鑰 | 每次 cron 執行 |
| **Disney Careers** | Hermes agent 用瀏覽器前往 disneycareers.com | Hermes 瀏覽器工具 | 每天下午 2 點 |
| **TikTok Careers** | Hermes agent 用瀏覽器前往 lifeattiktok.com/teams/design | Hermes 瀏覽器工具 | 每天下午 2 點 |
| **手動** | 直接編輯 jobs.json | 無 | 隨時 |

---

### 公司分類系統

`company_class` 欄位由 `update_jobs.py` 中的 `classify_company()` 自動設定：

- **enterprise** → 知名大公司（Reddit, Stripe, Disney, Figma, TikTok 等）
- **mid-small** → 預設值（未知的公司）
- **school** → 大專院校、學校
- **freelance** → 外包平台 / 獵頭公司（Lemon.io, IAPWE, A.Team 等）

若要新增公司到某分類，編輯 `update_jobs.py` 中的 `BIG_COMPANIES` 列表或 freelancers 列表。

---

### 雙語機制

- 網站頂部有 **EN / 中文** 切換按鈕
- 每個職缺同時包含 `en` 和 `zh` 欄位
- 若 `zh.desc` 為空，卡片會顯示英文
- UI 文字（篩選標籤、統計數字、按鈕）透過 `index.html` 中的 `<span class="en-text">` / `<span class="zh-text">` 實現雙語

---

### 常見問題

**Q: 推送後網站沒更新？**
- GitHub Pages 需要 1-3 分鐘部署
- 檢查：`https://github.com/rich520ricky-lab/art-jobs-board/actions`

**Q: 職缺資料亂掉或有重複？**
- 刪除 `jobs.json` 重新執行 `python3 update_jobs.py`（會抓全新資料）
- 再執行 `python3 extra_scraper.py` 恢復 Disney/TikTok 職缺

**Q: TikTok 爬不到職缺？**
- TikTok 求職頁面不時會改版
- 嘗試手動前往 `https://lifeattiktok.com/teams/design`
- 如果頁面佈局變了，Hermes agent 可能需要更新的操作說明

**Q: 要搬到新電腦？**
1. `git clone` 專案到新電腦
2. 安裝 Hermes Agent
3. 用 `cronjob create` 重新建立排程任務（見第四步）
4. 驗證：`python3 update_jobs.py` 執行無錯誤

---

*Last updated / 最後更新: May 08, 2026*