-- Partner-onboarding e2e audit run history (public www e2e cockpit, cron-driven).

create table if not exists public.partner_onboarding_audit_runs (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null,
  score integer not null check (score between 0 and 100),
  status text not null
    check (status in ('pass', 'fail', 'error')),
  critical_count integer not null default 0,
  high_count integer not null default 0,
  findings jsonb not null default '[]'::jsonb,
  run_at timestamptz not null default now()
);

create index if not exists idx_partner_onboarding_audit_runs_run_at
  on public.partner_onboarding_audit_runs (run_at desc);

create index if not exists idx_partner_onboarding_audit_runs_run
  on public.partner_onboarding_audit_runs (run_id, run_at desc);

-- Plain Postgres CI lacks Supabase API roles; create stub when missing.
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role nologin;
  end if;
end $$;

grant select, insert on public.partner_onboarding_audit_runs to service_role;

comment on table public.partner_onboarding_audit_runs is
  'Scheduled partner-onboarding e2e audit runs (commission/strategic partner funnel health) — one row per cron cycle.';
