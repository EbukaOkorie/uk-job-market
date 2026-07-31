from dotenv import load_dotenv
load_dotenv()

"""Daily collector. Source: Adzuna API, https://www.adzuna.co.uk/"""
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests, yaml

BASE = "https://api.adzuna.com/v1/api/jobs/gb/search"
APP_ID, APP_KEY = os.environ["ADZUNA_APP_ID"], os.environ["ADZUNA_APP_KEY"]
ROLES = ["data analyst", "data engineer", "data scientist",
         "business intelligence", "analytics"]
PAGES, PAUSE = 2, 3

session = requests.Session()
calls = 0

def fetch(page=1, **params):
    global calls
    p = {"app_id": APP_ID, "app_key": APP_KEY, "content-type": "application/json"}
    p.update(params)
    for attempt in range(3):
        time.sleep(PAUSE)
        try:
            r = session.get(f"{BASE}/{page}", params=p, timeout=30)
            calls += 1
            if r.status_code == 200:
                return r.json()
            print(f"  HTTP {r.status_code} {params}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  {e}", file=sys.stderr)
        time.sleep(5 * (attempt + 1))
    return None

run_at = datetime.now(timezone.utc)
out = Path("data/raw") / run_at.strftime("%Y-%m-%d")
out.mkdir(parents=True, exist_ok=True)

skills = [s for g in yaml.safe_load(open("skills.yml")).values() for s in g]
rows = []
for term in skills:
    live = fetch(what_phrase=term, results_per_page=1)
    new = fetch(what_phrase=term, results_per_page=1, max_days_old=1)
    rows.append({"term": term,
                 "live_count": live["count"] if live else None,
                 "new_count": new["count"] if new else None})
    print(f"  {term:<18} live {rows[-1]['live_count']}  new {rows[-1]['new_count']}")

postings, seen = [], set()
for role in ROLES:
    for page in range(1, PAGES + 1):
        d = fetch(page, what_phrase=role, results_per_page=50, sort_by="date")
        if not d:
            continue
        for j in d["results"]:
            if j["id"] not in seen:
                seen.add(j["id"])
                postings.append({**j, "_query": role})

meta = {"collected_at": run_at.isoformat(), "api_calls": calls, "source": "Adzuna API"}
(out / "skills.json").write_text(json.dumps({**meta, "skills": rows}, indent=2))
(out / "postings.json").write_text(json.dumps({**meta, "postings": postings}, indent=2))
print(f"\n{len(rows)} skills, {len(postings)} postings, {calls} calls")