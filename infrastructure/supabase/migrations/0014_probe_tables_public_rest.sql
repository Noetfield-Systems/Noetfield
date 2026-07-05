-- Expose probe tables via PostgREST (public schema — noetfield schema not in API).

create table if not exists public.probe_cron_receipts (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null,
  probe_name text not null,
  status text not null
    check (status in ('pass', 'fail', 'error')),
  receipt jsonb not null default '{}'::jsonb,
  checked_at timestamptz not null default now()
);

create table if not exists public.improvement_queue (
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

create index if not exists idx_public_probe_cron_receipts_probe_time
  on public.probe_cron_receipts (probe_name, checked_at desc);

create index if not exists idx_public_improvement_queue_status_created
  on public.improvement_queue (status, created_at desc);

grant select, insert on public.probe_cron_receipts to service_role;
grant select, insert, update on public.improvement_queue to service_role;

comment on table public.probe_cron_receipts is 'Probe cron receipts (REST-visible mirror of noetfield.probe_cron_receipts).';
comment on table public.improvement_queue is 'Improvement findings queue (REST-visible mirror).';
