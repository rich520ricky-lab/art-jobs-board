#!/usr/bin/env python3
"""
Extra scraper for Disney Careers and TikTok Careers.
This script is meant to be RUN INTERACTIVELY by Hermes agent using browser tools.
It can also store known job IDs and check if jobs.json already has them.

Usage: Hermes agent loads this file when doing manual scrape runs.
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(SCRIPT_DIR, "jobs.json")

# Known Disney Career search URLs for art/design roles
DISNEY_SEARCH_URLS = [
    "https://www.disneycareers.com/en/search-jobs/?q=artist+designer+animator+creative&sortBy=relevancy",
]

# Known TikTok teams pages with art/design roles
TIKTOK_TEAM_PAGES = [
    "https://lifeattiktok.com/teams/design",
    "https://lifeattiktok.com/teams/product",
    "https://lifeattiktok.com/teams/marketing",
]

# =============================================
# KNOWN JOB DATA (extracted from browser sessions)
# When new jobs are found via browser, add to this dict
# so they survive re-runs without losing data
# =============================================
KNOWN_DISNEY_JOBS = [
    {
        "en": {"title": "Crowds Artist", "company": "Walt Disney Animation Studios", "desc": "Create crowd simulations and agent-based animations for Disney animated features."},
        "zh": {"title": "群眾動畫師", "company": "Walt Disney Animation Studios", "desc": "為迪士尼動畫長片製作群眾模擬與角色動畫。"},
        "location": "Burbank, CA", "type": "On-site", "category": "Animation",
        "salary": "", "posted": "Feb 05, 2026", "link": "https://www.disneycareers.com/en/job/burbank/crowds-artist/391/91430667568",
        "featured": False, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Artist, Creative Development - Disney & Pixar Games", "company": "Disney", "desc": "Provide visual guidance and brand feedback for Disney and Pixar game projects."},
        "zh": {"title": "創意開發美術師 - Disney & Pixar 遊戲", "company": "Disney", "desc": "為 Disney 和 Pixar 遊戲專案提供視覺指導與品牌反饋。"},
        "location": "Glendale, CA", "type": "On-site", "category": "Concept Art",
        "salary": "", "posted": "Apr 23, 2026", "link": "https://www.disneycareers.com/en/job/glendale/artist-creative-development-disney-and-pixar-games/391/94304799488",
        "featured": False, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "VP-Creative Americas", "company": "Disney Experiences", "desc": "Lead creative vision and strategy for Disney Experiences across the Americas region."},
        "zh": {"title": "創意副總裁 - 美洲區", "company": "Disney Experiences", "desc": "領導美洲區 Disney Experiences 的創意願景與策略。"},
        "location": "Glendale, CA", "type": "On-site", "category": "Art Direction",
        "salary": "", "posted": "May 05, 2026", "link": "https://www.disneycareers.com/en/job/glendale/vp-creative-americas/391/91838125248",
        "featured": False, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Stereoscopic Layout Artist", "company": "Walt Disney Animation Studios", "desc": "Create stereoscopic 3D layouts and camera setups for animated feature films."},
        "zh": {"title": "立體佈局美術師", "company": "Walt Disney Animation Studios", "desc": "為動畫長片製作立體 3D 佈局與鏡頭設置。"},
        "location": "Burbank, CA", "type": "On-site", "category": "3D Art",
        "salary": "", "posted": "Mar 02, 2026", "link": "https://www.disneycareers.com/en/job/burbank/stereoscopic-layout-artist/391/92320928464",
        "featured": False, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "VFX Artist", "company": "Disney Experiences", "desc": "Create visual effects for Disney theme park attractions, shows, and experiences."},
        "zh": {"title": "視覺特效美術師", "company": "Disney Experiences", "desc": "為迪士尼主題樂園景點、表演和體驗製作視覺特效。"},
        "location": "Glendale, CA", "type": "On-site", "category": "VFX",
        "salary": "", "posted": "Apr 29, 2026", "link": "https://www.disneycareers.com/en/job/glendale/vfx-artist/391/94531855328",
        "featured": False, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Sr. Manager, Lead Concept Artist", "company": "Disney Experiences", "desc": "Lead concept art team for Disney park and resort creative development."},
        "zh": {"title": "資深經理 - 首席概念美術師", "company": "Disney Experiences", "desc": "領導迪士尼樂園與度假村創意開發的概念美術團隊。"},
        "location": "Glendale, CA", "type": "On-site", "category": "Concept Art",
        "salary": "", "posted": "Recently", "link": "https://www.disneycareers.com/en/job/glendale/sr-manager-lead-concept-artist/391/94344222272",
        "featured": True, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Freelance Graphic Artist", "company": "Disney (KABC)", "desc": "Create graphics for KABC television broadcasts and digital platforms."},
        "zh": {"title": "自由接案平面美術師", "company": "Disney (KABC)", "desc": "為 KABC 電視廣播和數位平台製作圖形。"},
        "location": "Glendale, CA", "type": "On-site", "category": "Graphic Design",
        "salary": "", "posted": "Recently", "link": "https://www.disneycareers.com/en/job/glendale/kabc-freelance-graphic-artist/391/93397165632",
        "featured": True, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Manager, Product Design - Apparel", "company": "Disney", "desc": "Lead product design for Disney apparel collections across brands."},
        "zh": {"title": "產品設計經理 - 服飾", "company": "Disney", "desc": "領導跨品牌的迪士尼服飾系列產品設計。"},
        "location": "Glendale, CA", "type": "On-site", "category": "Product Design",
        "salary": "", "posted": "Recently", "link": "https://www.disneycareers.com/en/job/glendale/manager-product-design-apparel/391/94000927568",
        "featured": True, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Art Director - Marvel Games", "company": "Marvel Entertainment (Disney)", "desc": "Drive artistic vision for Marvel Games titles across all platforms."},
        "zh": {"title": "藝術總監 - Marvel 遊戲", "company": "Marvel Entertainment (Disney)", "desc": "推動 Marvel 遊戲跨平台的藝術願景。"},
        "location": "Burbank, CA", "type": "On-site", "category": "Game Art",
        "salary": "", "posted": "Recently", "link": "https://www.disneycareers.com/en/job/burbank/art-director-marvel-games/391/83591725344",
        "featured": True, "new": False, "company_class": "enterprise"
    },
]

KNOWN_TIKTOK_JOBS = [
    {
        "en": {"title": "Senior Design Technologist, Design Foundation", "company": "TikTok", "desc": "Lead the design technology and design systems foundation for TikTok's product experience."},
        "zh": {"title": "資深設計技術師 - 設計基礎架構", "company": "TikTok", "desc": "領導 TikTok 產品體驗的設計技術與設計系統基礎架構。"},
        "location": "San Jose, CA", "type": "On-site", "category": "UI/UX",
        "salary": "", "posted": "Recently", "link": "https://lifeattiktok.com/search/7631650139656063285",
        "featured": True, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Content Designer, Ads", "company": "TikTok", "desc": "Design compelling ad content experiences for TikTok's advertising platform."},
        "zh": {"title": "內容設計師 - 廣告", "company": "TikTok", "desc": "為 TikTok 廣告平台設計引人入勝的廣告內容體驗。"},
        "location": "San Jose, CA", "type": "On-site", "category": "Graphic Design",
        "salary": "", "posted": "Recently", "link": "https://lifeattiktok.com/search/7553329183243143432",
        "featured": True, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Senior Content Designer, Ads", "company": "TikTok", "desc": "Lead content design strategy for TikTok's advertising products and campaigns."},
        "zh": {"title": "資深內容設計師 - 廣告", "company": "TikTok", "desc": "領導 TikTok 廣告產品的內容設計策略。"},
        "location": "San Jose, CA", "type": "On-site", "category": "Graphic Design",
        "salary": "", "posted": "Recently", "link": "https://lifeattiktok.com/search/7602793214941366581",
        "featured": True, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Product Designer (Creator) - TikTok UX", "company": "TikTok", "desc": "Design creator-facing product experiences for TikTok's global user base."},
        "zh": {"title": "產品設計師 (創作者) - TikTok UX", "company": "TikTok", "desc": "為 TikTok 全球用戶設計創作者面向的產品體驗。"},
        "location": "San Jose, CA", "type": "On-site", "category": "UI/UX",
        "salary": "", "posted": "Recently", "link": "https://lifeattiktok.com/search/7599799873770277125",
        "featured": True, "new": False, "company_class": "enterprise"
    },
    {
        "en": {"title": "Content Design Intern (TikTok-Design-Live) - 2026 Start", "company": "TikTok", "desc": "Create content design solutions for TikTok Live features as a design intern."},
        "zh": {"title": "內容設計實習生 (TikTok-Design-Live) - 2026", "company": "TikTok", "desc": "為 TikTok Live 功能製作內容設計解決方案的實習機會。"},
        "location": "Singapore", "type": "On-site", "category": "UI/UX",
        "salary": "", "posted": "Recently", "link": "https://lifeattiktok.com/search/7533134925695666440",
        "featured": True, "new": False, "company_class": "enterprise"
    },
]


def add_jobs_if_new(jobs_list):
    """Add jobs from a list into jobs.json, skipping duplicates. Returns count added."""
    if not os.path.exists(JOBS_FILE):
        print(f"  ❌ jobs.json not found at {JOBS_FILE}")
        return 0
    
    with open(JOBS_FILE) as f:
        jobs = json.load(f)
    
    existing_keys = set((j['en']['title'].lower().strip(), j['en']['company'].lower().strip()) for j in jobs)
    added = 0
    for j in jobs_list:
        key = (j['en']['title'].lower().strip(), j['en']['company'].lower().strip())
        if key not in existing_keys:
            existing_keys.add(key)
            jobs.append(j)
            added += 1
    
    if added > 0:
        with open(JOBS_FILE, 'w') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Added {added} new jobs")
    else:
        print(f"  ⏭️  No new jobs to add")
    
    return added


if __name__ == "__main__":
    print(f"{'='*50}")
    print(f"Disney + TikTok Job Scraper")
    print(f"{'='*50}")
    print(f"\n📋 Adding known Disney jobs...")
    disney_added = add_jobs_if_new(KNOWN_DISNEY_JOBS)
    
    print(f"\n📋 Adding known TikTok jobs...")
    tiktok_added = add_jobs_if_new(KNOWN_TIKTOK_JOBS)
    
    total = disney_added + tiktok_added
    print(f"\n{'='*50}")
    print(f"Total new: {total}")
    print(f"{'='*50}")