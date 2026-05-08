# Disney + TikTok Browser Scrape Guide
# Disney + TikTok 瀏覽器爬蟲操作指南

> Use this when you want to manually scrape the latest art/design jobs from Disney Careers and TikTok Careers.
> 當你想手動抓取 Disney Careers 和 TikTok Careers 的最新美術/設計職缺時使用。

---

## EN / English

### How Hermes Agent Scrapes These Sites

The Disney and TikTok career sites use JavaScript-heavy SPAs that block direct API calls. The only way to extract jobs is by **using a real browser** (Hermes browser tools). Here's the exact process:

### Step 1: Scrape Disney Careers

1. **Navigate to Disney search page:**
   ```
   https://www.disneycareers.com/en/search-jobs/?q=artist+designer+animator+creative&sortBy=relevancy
   ```

2. **Wait for the page to fully load** (job count should appear)

3. **Extract job links** by running this in the browser console:
   ```javascript
   Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => ({
     title: a.querySelector('h2')?.textContent?.trim(),
     company: a.querySelectorAll('p')[0]?.textContent?.trim(),
     location: a.querySelectorAll('p')[1]?.textContent?.trim(),
     date: a.querySelectorAll('p')[2]?.textContent?.trim(),
     href: a.href
   })).filter(x => x.href)
   ```

4. **For each NEW job** (not already in `jobs.json`), create a job entry:

   ```json
   {
     "en": { "title": "Job Title", "company": "Company Name", "desc": "Short description" },
     "zh": { "title": "中文職稱", "company": "公司名稱", "desc": "中文描述" },
     "location": "City, State",
     "type": "On-site",
     "category": "Animation",
     "company_class": "enterprise",
     "salary": "",
     "posted": "Recently",
     "link": "https://disneycareers.com/en/job/...",
     "featured": true,
     "new": true
   }
   ```

5. **Categories for Disney jobs:**
   - Crowds Artist → Animation
   - Concept Artist / Visual Development → Concept Art
   - VFX Artist → VFX
   - Layout Artist → 3D Art
   - Animator → Animation
   - Art Director → Game Art or Art Direction
   - Graphic / Product Designer → Graphic Design or Product Design

### Step 2: Scrape TikTok Careers

1. **Navigate to TikTok Design team page:**
   ```
   https://lifeattiktok.com/teams/design
   ```

2. **Scroll down** to the "Explore open roles in Design" section

3. **The job table shows:**
   - Title | Area of Work | Job Type | Location
   - Each row is a clickable link

4. **Extract jobs** — In the accessibility tree, the jobs appear as links like:
   ```
   lifeattiktok.com/search/7631650139656063285  → Senior Design Technologist, Design Foundation
   lifeattiktok.com/search/7553329183243143432  → Content Designer, Ads
   ```

5. **For each NEW job**, create entry with:
   - company: "TikTok"
   - company_class: "enterprise"
   - type: based on location (San Jose = On-site, Singapore = On-site)
   - category: based on title (Product Designer → UI/UX, Content Designer → Graphic Design)

6. **To search different keywords**, go to:
   ```
   https://lifeattiktok.com/search?keyword=YOUR_KEYWORD
   ```
   Then check "Design" in the Job Category filter and click Search.

### Step 3: Add Jobs & Deploy

```bash
# Add new jobs to jobs.json (edit the file or use extra_scraper.py)
cd ~/hermes/art-jobs-site
python3 extra_scraper.py

# Update last_updated.txt
echo "May 08, 2026" > last_updated.txt

# Git commit + push
git add jobs.json last_updated.txt
git commit -m "Add Disney+TikTok jobs"
git push

# Verify
curl -s -o /dev/null -w "%{http_code}" "https://rich520ricky-lab.github.io/art-jobs-board/"
# Should return 200
```

---

## ZH / 中文

### 為什麼要用瀏覽器爬？

Disney 和 TikTok 的求職網站都是 JavaScript SPA，直接調 API 會被擋。唯一能拿到職缺資料的方式是**使用真實瀏覽器操作**。

---

### 第一步：爬 Disney Careers

1. **前往 Disney 搜尋頁面：**
   ```
   https://www.disneycareers.com/en/search-jobs/?q=artist+designer+animator+creative&sortBy=relevancy
   ```

2. **等頁面完全載入**（會顯示職缺數量）

3. **提取職缺連結** — 在瀏覽器 Console 執行：
   ```javascript
   Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => ({
     title: a.querySelector('h2')?.textContent?.trim(),
     company: a.querySelectorAll('p')[0]?.textContent?.trim(),
     location: a.querySelectorAll('p')[1]?.textContent?.trim(),
     date: a.querySelectorAll('p')[2]?.textContent?.trim(),
     href: a.href
   })).filter(x => x.href)
   ```

4. **每個新職缺**（`jobs.json` 中沒有的）建立一個條目。

5. **分類建議：**
   - Crowds Artist → Animation
   - Concept Artist / Visual Development → Concept Art
   - VFX Artist → VFX
   - Layout Artist → 3D Art
   - Animator → Animation
   - Art Director → Game Art 或 Art Direction
   - Graphic / Product Designer → Graphic Design 或 Product Design

### 第二步：爬 TikTok Careers

1. **前往 TikTok Design 團隊頁面：**
   ```
   https://lifeattiktok.com/teams/design
   ```

2. **往下捲**到「Explore open roles in Design」區塊

3. **職缺表格**顯示：職稱 | 工作領域 | 職缺類型 | 地點
   每行都是一個可點擊的連結

4. **提取職缺：** 在 accessibility tree 中，職缺連結格式為：
   ```
   lifeattiktok.com/search/7631650139656063285  → Senior Design Technologist, Design Foundation
   ```

5. **每個新職缺**建立條目：
   - company: "TikTok"
   - company_class: "enterprise"
   - type: San Jose → On-site, 新加坡 → On-site
   - category: Product Designer → UI/UX, Content Designer → Graphic Design

6. **搜尋不同關鍵字：** 前往
   ```
   https://lifeattiktok.com/search?keyword=你的關鍵字
   ```
   勾選「Design」分類後按搜尋。

### 第三步：加入職缺並部署

```bash
cd ~/hermes/art-jobs-site
python3 extra_scraper.py    # 合併已知職缺（去重）
git add jobs.json last_updated.txt
git commit -m "加入 Disney+TikTok 新職缺"
git push
```

### 常用 TikTok 搜尋關鍵字

| 關鍵字 | 用途 |
|--------|------|
| `design` | 所有設計類職缺（202 筆） |
| `art` | 美術相關 |
| `graphic design` | 平面設計 |
| `visual` | 視覺設計 |
| `creative` | 創意相關 |
| `illustrator` | 插畫 |
| `animation` | 動畫 |

記得勾選 **Design** 分類來過濾出真正相關的職缺。

---

*Last updated / 最後更新: May 08, 2026*