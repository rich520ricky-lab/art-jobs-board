# Art & Design Job Tracker
# 美術設計職缺追蹤

A bilingual (EN / 中文) static job board that aggregates art & design job openings from multiple sources, automatically updated daily.

中英雙語靜態求職看板，彙整美術與設計相關職缺，每日自動更新。

**Live Site / 網站：** https://rich520ricky-lab.github.io/art-jobs-board/

---

## Data Sources / 資料來源

| Source / 來源 | Type / 類型 | Method / 方式 |
|---------------|-------------|----------------|
| Jobicy API | Design/Creative jobs | HTTP API (free) |
| Remotive API | Remote design jobs | HTTP API (free) |
| Disney Careers | Animation/Art at Disney, Pixar, Marvel | Browser scrape |
| TikTok Careers | Design team roles | Browser scrape |

## Features / 功能

- **Bilingual toggle** — switch between English and 中文
- **Company type filter** — Enterprise / Mid-Small / School / Freelance
- **Category, location, job type filters** — narrow down results
- **Detail modal** — view full job info before applying
- **Daily auto-update** — new jobs added automatically

## Tech Stack / 技術棧

- Static HTML/CSS/JS (no framework, no build step)
- GitHub Pages for hosting
- Python scripts for data collection
- Hermes Agent for cron scheduling

## Setup / 安裝

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for full setup and maintenance instructions.

完整安裝與維護說明請見 [SETUP_GUIDE.md](SETUP_GUIDE.md)。

## Structure / 目錄結構

```
├── index.html            # Bilingual job board
├── jobs.json             # All job data
├── last_updated.txt      # Update timestamp
├── update_jobs.py        # Daily API scraper (Jobicy + Remotive)
├── extra_scraper.py      # Disney+TikTok known job manager
├── DISNEY_TIKTOK_SCRAPE.md  # Step-by-step browser scrape guide
├── SETUP_GUIDE.md        # Full setup guide (EN/ZH)
└── README.md             # This file
```