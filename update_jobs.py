#!/usr/bin/env python3
"""
Art & Design Jobs Board - Daily Update Script
Fetches REAL art/design jobs from Jobicy API (free, no key needed).
"""
import json
import os
import subprocess
import re
import html
from datetime import datetime
from urllib.request import Request, urlopen

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(SCRIPT_DIR, "jobs.json")
LAST_UPDATED_FILE = os.path.join(SCRIPT_DIR, "last_updated.txt")

CATEGORY_KEYWORDS = {
    "Concept Art": ["concept artist", "concept art", "visual development", "storyboard"],
    "Animation": ["animator", "animation", "2d animator", "3d animator"],
    "3D Art": ["3d artist", "3d modeler", "environment artist", "character artist", "texture", "rigging", "shader"],
    "Game Art": ["game artist", "technical artist", "game design", "gameplay", "level design"],
    "VFX": ["visual effects", "vfx artist", "compositor", "lighting artist"],
    "Motion Design": ["motion designer", "motion graphics"],
    "Graphic Design": ["graphic designer", "graphic design", "brand designer", "brand design"],
    "UI/UX": ["ui designer", "ux designer", "product designer", "interaction designer", "ux research"],
    "Art Direction": ["art director", "creative director"],
    "Illustration": ["illustrator", "illustration"],
    "Product Design": ["product designer", "industrial designer"],
    "Education": ["art teacher", "art instructor", "art professor"],
}

LOCATION_KEYWORDS = {
    "Los Angeles, CA": ["los angeles", "la ca", "burbank", "glendale", "culver city", "santa monica", "pasadena"],
    "San Francisco, CA": ["san francisco", "sf ca", "bay area", "oakland", "menlo park"],
    "New York, NY": ["new york", "nyc", "brooklyn", "manhattan"],
    "Seattle, WA": ["seattle", "bellevue", "redmond"],
    "Austin, TX": ["austin", "texas"],
    "Remote": ["remote", "anywhere", "work from home"],
    "London, GB": ["london", "uk", "united kingdom"],
    "Vancouver, Canada": ["vancouver"],
}

def classify_category(title, desc=""):
    text = (title + " " + desc).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category
    return "Graphic Design"

def parse_location(raw):
    if not raw:
        return "Remote"
    raw_lower = raw.lower()
    for loc, aliases in LOCATION_KEYWORDS.items():
        for alias in aliases:
            if alias in raw_lower:
                return loc
    if "remote" in raw_lower or "anywhere" in raw_lower or "home" in raw_lower:
        return "Remote"
    return raw.strip()

def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:300]

def days_ago_str(date_str):
    if not date_str:
        return "Recently"
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"]:
        try:
            d = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
            diff = (datetime.now() - d).days
            if diff < 0: return "Today"
            if diff == 0: return "Today"
            if diff == 1: return "1 day ago"
            return f"{diff} days ago"
        except:
            continue
    return "Recently"

def is_new(posted):
    if not posted: return False
    return posted in ["Today", "1 day ago"] or "hours ago" in posted or "hour ago" in posted

def job_key(j):
    en = j.get("en", {})
    return (en.get("title", "").lower().strip(), en.get("company", "").lower().strip())

def merge_jobs(existing, new_jobs):
    existing_keys = set()
    for j in existing:
        existing_keys.add(job_key(j))
    added = 0
    for j in new_jobs:
        key = job_key(j)
        if key not in existing_keys and key[0] and key[1]:
            existing_keys.add(key)
            existing.append(j)
            added += 1
    return existing, added

def fetch_jobicy():
    """Fetch jobs from Jobicy API"""
    jobs = []
    tags = ["design", "art", "creative"]
    
    for tag in tags:
        try:
            url = f"https://jobicy.com/api/v2/remote-jobs?count=15&tag={tag}"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            
            for item in data.get("jobs", []):
                title = item.get("jobTitle", "")
                company = item.get("companyName", "")
                
                # Skip non-design jobs
                industries = [x.lower() for x in item.get("jobIndustry", [])]
                if not any(kw in str(industries) for kw in ["design", "creative", "art", "game", "animation"]):
                    continue
                
                desc = clean_html(item.get("jobDescription", "") or item.get("jobExcerpt", "") or "")
                job_url = item.get("url", "")
                geo = item.get("jobGeo", "")
                date_raw = item.get("pubDate", "")
                posted = days_ago_str(date_raw)
                
                location = parse_location(geo)
                category = classify_category(title, desc)
                
                # Determine job type from location
                if "hybrid" in geo.lower():
                    job_type = "Hybrid"
                elif "remote" in geo.lower() or geo.lower() in ["remote", "anywhere"]:
                    job_type = "Remote"
                else:
                    job_type = "On-site"
                
                salary = ""
                s_min = item.get("salaryMin")
                s_max = item.get("salaryMax")
                if s_min and s_max:
                    salary = f"${int(s_min):,}-${int(s_max):,}/yr"
                elif s_min:
                    salary = f"From ${int(s_min):,}/yr"
                
                jobs.append({
                    "en": {"title": title, "company": company, "desc": desc},
                    "zh": {"title": title, "company": company, "desc": ""},
                    "location": location,
                    "type": job_type,
                    "category": category,
                    "salary": salary,
                    "posted": posted,
                    "link": job_url,
                    "featured": is_new(posted),
                    "new": is_new(posted)
                })
        except Exception as e:
            print(f"  Jobicy ({tag}): {e}")
    
    print(f"  Jobicy: {len(jobs)} jobs")
    return jobs

def main():
    print(f"\n{'='*50}")
    print(f"Art & Design Jobs Board - Daily Update")
    print(f"{'='*50}\n")
    
    existing_jobs = []
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r") as f:
            existing_jobs = json.load(f)
    
    print(f"📋 Existing jobs: {len(existing_jobs)}")
    print(f"\n🔍 Fetching new jobs...\n")
    
    print("1. Jobicy API...")
    all_new = fetch_jobicy()
    
    print(f"\n📊 Total fetched: {len(all_new)} raw jobs")
    
    merged, added = merge_jobs(existing_jobs, all_new)
    
    print(f"➕ New jobs added: {added}")
    print(f"📊 Total jobs: {len(merged)}")
    
    with open(JOBS_FILE, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    hour_str = now.strftime("%I:%M %p").lstrip("0")
    with open(LAST_UPDATED_FILE, "w") as f:
        f.write(f"{date_str}, {hour_str}")
    print(f"🕐 Last updated: {date_str}")
    
    # Git push
    os.chdir(SCRIPT_DIR)
    try:
        r = subprocess.run(["git", "add", "jobs.json", "last_updated.txt"], capture_output=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if r.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"Auto-update: +{added} jobs ({date_str})"], capture_output=True)
            push = subprocess.run(["git", "push"], capture_output=True, text=True)
            if push.returncode == 0:
                print(f"🚀 Deployed to GitHub Pages!")
            else:
                print(f"⚠️  Push: {push.stdout[:200]}{push.stderr[:200]}")
        else:
            print(f"⏭️  No changes to commit")
    except Exception as e:
        print(f"⚠️  Git error: {e}")
    
    return added

if __name__ == "__main__":
    main()