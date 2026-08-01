create table if not exists skill_counts (
    collected_on date    not null,
    term         text    not null,
    skill_group  text,
    live_count   integer,
    new_count    integer,
    primary key (collected_on, term)
);

create table if not exists postings (
    id                  text primary key,
    title               text,
    company             text,
    category            text,
    contract_type       text,
    contract_time       text,
    salary_min          numeric,
    salary_max          numeric,
    salary_is_predicted boolean,
    location_display    text,
    region              text,
    area                text[],
    created             timestamptz,
    first_seen          date not null,
    last_seen           date not null,
    payload             jsonb not null
);

create index if not exists idx_postings_created on postings (created);
create index if not exists idx_postings_region  on postings (region);
create index if not exists idx_skill_counts_term on skill_counts (term);