"""Export curated views to CSV for the BI layer."""
import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv()
out = Path("data/exports")
out.mkdir(parents=True, exist_ok=True)

VIEWS = ["v_skill_trend", "v_skill_latest", "v_salary",
         "v_salary_by_region", "v_posting_lifespan"]

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    for v in VIEWS:
        path = out / f"{v}.csv"
        with conn.cursor().copy(f"copy (select * from {v}) to stdout with csv header") as copy:
            path.write_bytes(b"".join(copy))
        print(f"{v}: {sum(1 for _ in path.open()) - 1} rows")
    