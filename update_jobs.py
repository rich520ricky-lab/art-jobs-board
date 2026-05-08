#!/usr/bin/env python3
"""
Art & Design Jobs Board - Multi-source scraper
Fetches real jobs from multiple free sources.
"""
import json
import os
import re
import subprocess
import html
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(SCRIPT_DIR, "jobs.json")
LAST_UPDATED_FILE = os.path.join(SCRIPT_DIR, "last_updated.txt")

CATEGORY_KEYWORDS = {
    "Concept Art": ["concept artist", "concept art", "visual development", "storyboard artist"],
    "Animation": ["animator", "animation", "2d animator", "3d animator", "motion capture"],
    "3D Art": ["3d artist", "3d modeler", "environment artist", "character artist", "texture artist", "rigging artist", "shader"],
    "Game Art": ["game artist", "technical artist", "game designer", "gameplay designer", "level designer"],
    "VFX": ["visual effects", "vfx artist", "compositor", "lighting artist", "fx artist"],
    "Motion Design": ["motion designer", "motion graphics", "mograph"],
    "Graphic Design": ["graphic designer", "graphic design", "brand designer", "brand design", "print designer"],
    "UI/UX": ["ui designer", "ux designer", "product designer", "interaction designer", "ux researcher", "ui/ux"],
    "Art Direction": ["art director", "creative director"],
    "Illustration": ["illustrator", "illustration"],
    "Product Design": ["product designer", "industrial designer", "service designer"],
    "Education": ["art teacher", "art instructor", "art professor", "lecturer"],
}

# =============================================
# COMPANY CLASSIFICATION
# =============================================
BIG_COMPANIES = [
    "reddit inc", "reddit", "amazon", "stripe", "figma", "samsara",
    "tripadvisor", "toast", "kraken", "collibra", "marqeta", "deel",
    "cd projekt", "telus", "veeam", "disney", "marvel",
    "mount sinai health",
]

SCHOOLS = [
    "university", "college", "school", "institute", "academy",
    "education", "teaching",
]

def classify_company(company_name):
    """Classify a company into: enterprise, mid-small, school, freelance"""
    name_lower = company_name.lower().strip()
    
    # Check schools
    for kw in SCHOOLS:
        if kw in name_lower:
            return "school"
    
    # Check big companies
    for bc in BIG_COMPANIES:
        if bc in name_lower:
            return "enterprise"
    
    # Check freelance platforms / staffing agencies
    freelancers = ["freelancer", "upwork", "fiverr", "iapwe", "lemon.io",
                   "mitre media", "coalition technologies", "remote star",
                   "a.team", "bulldog digital media", "sanctuary computer"]
    for fl in freelancers:
        if fl in name_lower:
            return "freelance"
    
    # Default: mid-small
    return "mid-small"


def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:250]

def classify(text):
    """Classify into a category based on title + description"""
    text_lower = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in text_lower:
                return cat
    return "Graphic Design"

def days_ago(d):
    diff = (datetime.now() - d).days
    if diff <= 0: return "Today"
    if diff == 1: return "1 day ago"
    return f"{diff} days ago"

def job_key(j):
    return (j["en"]["title"].lower().strip(), j["en"]["company"].lower().strip())

def merge(existing, new_jobs):
    keys = set(job_key(j) for j in existing)
    added = 0
    for j in new_jobs:
        k = job_key(j)
        if k not in keys and k[0] and k[1]:
            keys.add(k)
            existing.append(j)
            added += 1
    return existing, added

# =============================================
# SOURCE 1: Jobicy API
# =============================================
def fetch_jobicy():
    jobs = []
    tags = ["design", "art", "creative"]
    seen = set()
    for tag in tags:
        try:
            url = f"https://jobicy.com/api/v2/remote-jobs?count=20&tag={tag}"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            for item in data.get("jobs", []):
                title = item.get("jobTitle", "")
                company = item.get("companyName", "")
                key = (title.lower(), company.lower())
                if key in seen:
                    continue
                seen.add(key)
                desc = clean_html(item.get("jobExcerpt", "") or item.get("jobDescription", "") or "")
                geo = item.get("jobGeo", "")
                date_raw = item.get("pubDate", "")
                posted = days_ago(datetime.strptime(date_raw[:19], "%Y-%m-%dT%H:%M:%S")) if date_raw else "Recently"
                loc = "Remote"
                if geo and geo.lower() not in ["remote", "anywhere", "worldwide"]:
                    loc = geo.strip()
                jtype = "Remote"
                if geo and "hybrid" in geo.lower():
                    jtype = "Hybrid"
                sal = ""
                smin, smax = item.get("salaryMin"), item.get("salaryMax")
                if smin and smax:
                    sal = f"${int(smin):,}-${int(smax):,}/yr"
                url_link = item.get("url", "")
                cat = classify(title + " " + desc)
                cc = classify_company(company)
                jobs.append({
                    "en": {"title": title, "company": company, "desc": desc},
                    "zh": {"title": title, "company": company, "desc": ""},
                    "location": loc, "type": jtype, "category": cat, "company_class": cc,
                    "salary": sal, "posted": posted, "link": url_link,
                    "featured": posted in ["Today", "1 day ago"],
                    "new": posted in ["Today", "1 day ago"]
                })
        except Exception as e:
            print(f"  Jobicy ({tag}): {e}")
    print(f"  Jobicy: {len(jobs)} jobs")
    return jobs

# =============================================
# SOURCE 2: Remotive API (remote design jobs)
# =============================================
def fetch_remotive():
    jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs?category=design&limit=20"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        for item in data.get("jobs", []):
            title = item.get("title", "")
            company = item.get("company_name", "")
            desc = clean_html(item.get("description", "") or "")
            loc = item.get("candidate_required_location", "Worldwide")
            if "worldwide" in loc.lower():
                loc = "Remote"
            sal = item.get("salary", "") or ""
            url_link = item.get("url", "")
            date_raw = item.get("publication_date", "")
            posted = days_ago(datetime.strptime(date_raw[:19], "%Y-%m-%dT%H:%M:%S")) if date_raw else "Recently"
            cat = classify(title + " " + desc)
            cc = classify_company(company)
            jtype = "Remote"
            jobs.append({
                "en": {"title": title, "company": company, "desc": desc},
                "zh": {"title": title, "company": company, "desc": ""},
                "location": loc, "type": jtype, "category": cat, "company_class": cc,
                "salary": sal, "posted": posted, "link": url_link,
                "featured": posted in ["Today", "1 day ago"],
                "new": posted in ["Today", "1 day ago"]
            })
    except Exception as e:
        print(f"  Remotive: {e}")
    print(f"  Remotive: {len(jobs)} jobs")
    return jobs

# =============================================
# SOURCE 3: LinkedIn RSS via scraping
# =============================================
def fetch_linkedin_rss():
    """LinkedIn jobs via Google cache / RSS"""
    jobs = []
    queries = [
        "concept+artist", "graphic+designer", "animator", "ux+designer",
        "motion+designer", "art+director", "illustrator", "game+artist",
        "3d+artist", "vfx+artist", "product+designer", "brand+designer"
    ]
    seen_titles = set()
    
    for q in queries:
        try:
            # Try Indeed's RSS with different locations
            for loc in ["remote", "los+angeles", "new+york"]:
                url = f"https://rss.indeed.com/rss?q={q}&l={loc}"
                req = Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
                try:
                    with urlopen(req, timeout=8) as r:
                        content = r.read().decode()
                    # Simple RSS parsing
                    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
                    for item in items:
                        title_m = re.search(r'<title>(.*?)</title>', item)
                        desc_m = re.search(r'<description>(.*?)</description>', item)
                        link_m = re.search(r'<link>(.*?)</link>', item)
                        if not title_m or not link_m:
                            continue
                        title = clean_html(title_m.group(1))
                        desc = clean_html(desc_m.group(1)) if desc_m else ""
                        link = link_m.group(1).strip()
                        
                        # Extract company from title (Indeed format: "Title - Company - Location")
                        parts = title.split(" - ")
                        if len(parts) >= 2:
                            company = parts[-2].strip() if len(parts) >= 2 else parts[0].strip()
                            title_clean = parts[0].strip()
                            job_loc = parts[-1].strip() if len(parts) >= 3 else loc.replace("+", " ").title()
                        else:
                            company = "Unknown"
                            title_clean = title
                            job_loc = loc.replace("+", " ").title()
                        
                        t_key = title_clean.lower()[:60]
                        if t_key in seen_titles:
                            continue
                        seen_titles.add(t_key)
                        
                        cat = classify(title_clean + " " + desc)
                        jtype = "Remote" if "remote" in job_loc.lower() else "On-site"
                        
                        jobs.append({
                            "en": {"title": title_clean, "company": company, "desc": desc},
                            "zh": {"title": title_clean, "company": company, "desc": ""},
                            "location": job_loc, "type": jtype, "category": cat,
                            "salary": "", "posted": "Today",
                            "link": link, "featured": True, "new": True
                        })
                except:
                    pass
        except:
            pass
    
    print(f"  Indeed RSS: {len(jobs)} jobs")
    return jobs

# =============================================
# MAIN
# =============================================
def main():
    print(f"\n{'='*50}")
    print(f"Art & Design Jobs Board - Daily Multi-Source Update")
    print(f"{'='*50}\n")
    
    existing = []
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r") as f:
            existing = json.load(f)
    
    print(f"📋 Existing jobs: {len(existing)}")
    print(f"\n🔍 Fetching new jobs...\n")
    
    all_new = []
    print("1. Jobicy...")
    all_new.extend(fetch_jobicy())
    print("2. Remotive...")
    all_new.extend(fetch_remotive())
    print("3. Indeed RSS...")
    all_new.extend(fetch_linkedin_rss())
    
    print(f"\n📊 Total fetched: {len(all_new)} raw jobs")
    
    before = len(existing)
    merged, added = merge(existing, all_new)
    
    print(f"➕ New unique jobs added: {added}")
    print(f"📊 Total jobs: {len(merged)}")
    
    with open(JOBS_FILE, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    with open(LAST_UPDATED_FILE, "w") as f:
        f.write(date_str)
    print(f"🕐 Last updated: {date_str}")
    
    os.chdir(SCRIPT_DIR)
    try:
        subprocess.run(["git", "add", "jobs.json", "last_updated.txt"], capture_output=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if r.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"Auto-update: +{added} jobs ({date_str})"], capture_output=True)
            push = subprocess.run(["git", "push"], capture_output=True, text=True)
            if push.returncode == 0:
                print(f"🚀 Deployed to GitHub Pages!")
            else:
                print(f"⚠️  Push err: {push.stderr[:200]}")
        else:
            print(f"⏭️  No changes")
    except Exception as e:
        print(f"⚠️  Git: {e}")
    
    return added

if __name__ == "__main__":
    main()