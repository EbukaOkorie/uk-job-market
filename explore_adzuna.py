import requests, os, yaml

APP_ID, APP_KEY = os.environ["ADZUNA_APP_ID"], os.environ["ADZUNA_APP_KEY"]
BASE = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

skills = [s for group in yaml.safe_load(open("skills.yml")).values() for s in group]

for term in skills:
    r = requests.get(BASE, params={
        "app_id": APP_ID, "app_key": APP_KEY, "results_per_page": 3,
        "what_phrase": term, "content-type": "application/json"}, timeout=30)
    d = r.json()
    titles = " | ".join(j["title"][:40] for j in d["results"])
    print(f"{term:<18} {d['count']:>6}   {titles}")