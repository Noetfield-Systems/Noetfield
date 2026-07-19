-- Enterprise intake qualification payload (noetfield.enterprise-intake-qualified.v0.1).

set search_path = noetfield, public;

alter table public_intakes
  add column if not exists qualification_json jsonb;

comment on column public_intakes.qualification_json is
  'Deterministic enterprise intake qualification (tier, fit_score, urgency, next_step, owner_sla_hours).';
