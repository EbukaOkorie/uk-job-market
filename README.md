# UK Tech Job Market Tracker

Automated daily pipeline tracking skill demand and salaries in UK job
postings. Data from the Adzuna API.

Dashboard: [Tableau Public](https://public.tableau.com/authoring/UKTechJobMarketTracker/Dashboard1#1)

## Architecture

GitHub Actions runs daily at 06:00 UTC:

1. `collect.py` queries the Adzuna API and writes raw JSON to `data/raw/`
2. `load.py` loads it into Postgres (Neon) via `sql/schema.sql`
3. `sql/views.sql` handles transformation and aggregation
4. `export.py` writes curated CSVs to `data/exports/` for the BI layer

Transformation lives in SQL rather than in the BI tools so the logic is
readable in this repo rather than buried in a binary workbook.

## What the data measures

Skill demand comes from Adzuna result counts per search term, not from
parsing job descriptions. The API truncates descriptions to 500
characters, so text extraction would only see the opening paragraph of
each advert. Counting via the search index reads the full text.

Two measures are collected per skill: live adverts mentioning it, and
adverts posted in the last day.

## Known limitations

Descriptions are capped at 500 characters, so no skill extraction from
free text.

No historical backfill. Counts cover live adverts only, so older
adverts that have expired are already absent. Anything not collected on
the day is lost.

Around half of Adzuna salary figures are their own model estimates
rather than employer-stated. All salary analysis filters to stated
figures via `salary_is_predicted`.

Spark is untrackable. "spark" collides with ordinary English usage and
"apache spark" appears in only a fraction of relevant adverts, so
neither gives a usable figure. The term was dropped.

Regions with fewer than 15 stated salaries are excluded rather than
charted on thin samples.

Salary figures outside 15,000 to 400,000 are dropped, since day rates
and hourly rates sometimes appear in the same field. This removed
around 4% of stated salaries.

Tableau Public has no scheduled refresh on the free tier, so that
dashboard is updated manually. Power BI handles the automated refresh.

## Attribution

Job data from the Adzuna API, adzuna.co.uk. Aggregate figures only; no
individual adverts are republished.
