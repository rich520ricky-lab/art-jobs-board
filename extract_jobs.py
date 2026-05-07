#!/usr/bin/env python3
"""Extract jobsData from index.html and save as jobs.json"""
import re
import json

with open("index.html", "r") as f:
    text = f.read()

start = text.index("const jobsData = [") + len("const jobsData = [")
end = text.index("];", start)
jobs_js = text[start:end]

# Remove JS comments
jobs_js = re.sub(r'//.*\n', '\n', jobs_js)

# Step 1: Quote all JS-style keys (word chars before colon, inside objects)
# Strategy: replace each key that looks like `en:` or `title:` with `"en"` etc
# But avoid quoting things that are already inside string literals
# Simple approach: use re.sub with a function that checks context
def quote_key(m):
    return f'"{m.group(1)}":'

jobs_js = re.sub(r'(\w[\w]*)\s*:\s*(?=[^"]*(?:"[^"]*"[^"]*)*$)', lambda m: f'"{m.group(1)}":', jobs_js)

# Fix boolean/true/false/null to lowercase
jobs_js = jobs_js.replace('true', 'true').replace('false', 'false')
# Actually that's already fine. Fix trailing commas
jobs_js = re.sub(r',\s*}', '}', jobs_js)
jobs_js = re.sub(r',\s*]', ']', jobs_js)

with open("/tmp/jobs_debug.txt", "w") as f:
    f.write(jobs_js[:2000])

try:
    jobs = json.loads('[' + jobs_js + ']')
    with open("jobs.json", "w") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"✅ Extracted {len(jobs)} jobs to jobs.json")
except Exception as e:
    print(f"❌ Error: {e}")
    # Find the problematic line
    lines = jobs_js.split('\n')
    for i, line in enumerate(lines):
        try:
            json.loads('[' + '\n'.join(lines[:i+1]) + ']')
        except Exception as e2:
            print(f"  Line {i+1}: {str(e2)[:80]}")
            print(f"  Content: {line[:100]}")
            break