create or replace view v_skill_trend as
select collected_on, term, skill_group, live_count, new_count,
       live_count - lag(live_count) over (partition by term order by collected_on) as live_change,
       round(100.0 * new_count / nullif(sum(new_count) over (partition by collected_on), 0), 2) as new_share_pct
from skill_counts
where term <> 'apache spark';

create or replace view v_skill_latest as
select term, skill_group, live_count, new_count,
       rank() over (order by live_count desc) as rank_live,
       rank() over (order by new_count  desc) as rank_new
from skill_counts
where collected_on = (select max(collected_on) from skill_counts)
and term <> 'apache spark';

create or replace view v_salary as
select id, title, company, category, contract_type, contract_time,
       region, created, first_seen, last_seen, salary_min, salary_max,
       (salary_min + salary_max) / 2 as salary_mid
from postings
where not salary_is_predicted
  and salary_min between 15000 and 400000;

create or replace view v_salary_by_region as
select region, count(*) as n,
       round(percentile_cont(0.25) within group (order by salary_mid)) as p25,
       round(percentile_cont(0.50) within group (order by salary_mid)) as median,
       round(percentile_cont(0.75) within group (order by salary_mid)) as p75
from v_salary
where region is not null
group by region
having count(*) >= 15;

create or replace view v_posting_lifespan as
select id, title, company, region, first_seen, last_seen,
       (last_seen - first_seen) + 1 as days_visible
from postings;