"""Load collected JSON into Postgres. Idempotent, safe to rerun."""
import json, os
from pathlib import Path
import psycopg, yaml
from dotenv import load_dotenv

load_dotenv()
DB = os.environ["DATABASE_URL"]

groups = yaml.safe_load(open("skills.yml"))
group_of = {term: g for g, terms in groups.items() for term in terms}

with psycopg.connect(DB) as conn:
    conn.execute(Path("sql/schema.sql").read_text())

    for day_dir in sorted(Path("data/raw").iterdir()):
        day = day_dir.name

        skills = json.loads((day_dir / "skills.json").read_text())
        rows = [(day, s["term"], group_of.get(s["term"]),
                 s["live_count"], s["new_count"]) for s in skills["skills"]]
        conn.cursor().executemany("""
            insert into skill_counts
                (collected_on, term, skill_group, live_count, new_count)
            values (%s, %s, %s, %s, %s)
            on conflict (collected_on, term) do update set
                live_count = excluded.live_count,
                new_count  = excluded.new_count,
                skill_group = excluded.skill_group
        """, rows)

        posts = json.loads((day_dir / "postings.json").read_text())
        rows = []
        for j in posts["postings"]:
            area = j.get("location", {}).get("area", [])
            rows.append((
                j["id"], j.get("title"),
                j.get("company", {}).get("display_name"),
                j.get("category", {}).get("tag"),
                j.get("contract_type"), j.get("contract_time"),
                j.get("salary_min"), j.get("salary_max"),
                j.get("salary_is_predicted") == "1",
                j.get("location", {}).get("display_name"),
                area[1] if len(area) > 1 else None,
                area, j.get("created"), day, day, json.dumps(j),
            ))
        conn.cursor().executemany("""
            insert into postings (id, title, company, category,
                contract_type, contract_time, salary_min, salary_max,
                salary_is_predicted, location_display, region, area,
                created, first_seen, last_seen, payload)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on conflict (id) do update set
                last_seen = excluded.last_seen
        """, rows)

        print(f"{day}: {len(skills['skills'])} skills, {len(posts['postings'])} postings")

    conn.commit()