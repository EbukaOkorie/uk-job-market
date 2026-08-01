import os, psycopg
from dotenv import load_dotenv
load_dotenv()

Q = [
 ("row counts",
  "select (select count(*) from skill_counts) sc, (select count(*) from postings) p"),
 ("region coverage", """
    select coalesce(region,'(none)') r, count(*) n
    from postings group by 1 order by n desc limit 8"""),
 ("salary presence", """
    select count(*) total,
           count(salary_min) has_salary,
           count(*) filter (where salary_is_predicted) predicted
    from postings"""),
 ("stated salary by contract", """
    select contract_time, count(*) n, round(avg(salary_min)) avg_min
    from postings
    where salary_min is not null and not salary_is_predicted
    group by 1 order by n desc"""),
 ("top new_count", """
    select term, live_count, new_count
    from skill_counts order by new_count desc nulls last limit 5"""),
]

with psycopg.connect(os.environ["DATABASE_URL"]) as c:
    for label, sql in Q:
        print(f"\n{label}")
        cur = c.execute(sql)
        cols = [d.name for d in cur.description]
        for row in cur.fetchall():
            print("  ", dict(zip(cols, row)))