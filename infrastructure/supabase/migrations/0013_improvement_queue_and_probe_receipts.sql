-- Improvement queue + probe cron receipts (15-min worker → Supabase).

set search_path = noetfield, public;

create table if not exists improvement_queue (
  id uuid primary key default gen_random_uuid(),
  finding text not null,
  source text not null,
  expected_roi text,
  machine_safe boolean not null default false,
  status text not null default 'open'
    check (status in ('open', 'in_progress', 'resolved', 'dismissed')),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists probe_cron_receipts (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null,
  probe_name text not null,
  status text not null
    check (status in ('pass', 'fail', 'error')),
  receipt jsonb not null default '{}'::jsonb,
  checked_at timestamptz not null default now()
);

create index if not exists idx_improvement_queue_status_created
  on improvement_queue (status, created_at desc);

create index if not exists idx_improvement_queue_source_created
  on improvement_queue (source, created_at desc);

create index if not exists idx_probe_cron_receipts_probe_time
  on probe_cron_receipts (probe_name, checked_at desc);

create index if not exists idx_probe_cron_receipts_run
  on probe_cron_receipts (run_id, checked_at desc);

comment on table improvement_queue is 'Actionable findings from automated probes (machine_safe gates auto-fix lanes).';
comment on table probe_cron_receipts is '15-min probe cron receipts — intake, greeting, drift, uptime.';

-- Plain Postgres CI lacks Supabase API roles; create stub when missing.
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role nologin;
  end if;
end $$;

grant usage on schema noetfield to service_role;
grant select, insert, update on improvement_queue to service_role;
grant select, insert on probe_cron_receipts to service_role;
