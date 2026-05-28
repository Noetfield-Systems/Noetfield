-- Noetfield v3.1 foundational database architecture.
-- This schema is layered intentionally. It is not a generic app database.
-- It is the memory substrate for governed ambient intelligence.

create extension if not exists "pgcrypto";
create extension if not exists "uuid-ossp";
create extension if not exists vector;

create schema if not exists noetfield;

set search_path = noetfield, public;

-- ---------------------------------------------------------------------------
-- Shared enterprise foundation
-- ---------------------------------------------------------------------------

create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  legal_name text,
  primary_domain text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists tenants (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id),
  name text not null,
  deployment_mode text not null default 'saas'
    check (deployment_mode in ('saas', 'single_tenant', 'enterprise_cloud', 'isolated', 'sovereign')),
  data_region text not null default 'default',
  status text not null default 'active'
    check (status in ('active', 'suspended', 'offboarding')),
  configuration jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists tenant_memberships (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  subject_id text not null,
  subject_type text not null default 'human'
    check (subject_type in ('human', 'service', 'ai', 'inspector')),
  roles text[] not null default '{}',
  attributes jsonb not null default '{}'::jsonb,
  status text not null default 'active'
    check (status in ('active', 'disabled', 'pending')),
  created_at timestamptz not null default now(),
  unique (tenant_id, subject_id)
);

-- ---------------------------------------------------------------------------
-- Layer 1: Raw Signal Layer
-- Immutable ingestion memory. Preserve original truth.
-- ---------------------------------------------------------------------------

create table if not exists signal_sources (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  source_type text not null,
  name text not null,
  uri text,
  trust_tier text not null default 'unverified'
    check (trust_tier in ('unverified', 'trusted', 'authoritative', 'restricted')),
  ingestion_policy jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists ingestion_runs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  signal_source_id uuid references signal_sources(id),
  status text not null default 'started'
    check (status in ('started', 'completed', 'failed', 'cancelled')),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  actor_id text not null,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists crawl_jobs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  signal_source_id uuid references signal_sources(id),
  ingestion_run_id uuid references ingestion_runs(id),
  target_uri text not null,
  crawl_policy jsonb not null default '{}'::jsonb,
  status text not null default 'queued'
    check (status in ('queued', 'running', 'completed', 'failed', 'cancelled')),
  scheduled_at timestamptz not null default now(),
  started_at timestamptz,
  completed_at timestamptz
);

create table if not exists raw_documents (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  ingestion_run_id uuid references ingestion_runs(id),
  crawl_job_id uuid references crawl_jobs(id),
  source_uri text,
  content_type text,
  storage_uri text,
  content_hash text not null,
  raw_metadata jsonb not null default '{}'::jsonb,
  captured_at timestamptz not null default now()
);

create table if not exists signals (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  signal_source_id uuid references signal_sources(id),
  ingestion_run_id uuid references ingestion_runs(id),
  raw_document_id uuid references raw_documents(id),
  signal_type text not null,
  source_event_id text,
  observed_at timestamptz not null,
  received_at timestamptz not null default now(),
  payload jsonb not null,
  payload_hash text not null,
  embedding vector(1536),
  provenance jsonb not null default '{}'::jsonb
);

-- ---------------------------------------------------------------------------
-- Layer 2: Normalized Intelligence Layer
-- Structured extracted intelligence.
-- ---------------------------------------------------------------------------

create table if not exists industries (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  taxonomy text not null default 'noetfield'
);

create table if not exists geographies (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  geography_type text not null
);

create table if not exists entities (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  entity_type text not null,
  canonical_name text not null,
  aliases text[] not null default '{}',
  source_refs uuid[] not null default '{}',
  confidence numeric(5,4) not null default 0.5000 check (confidence >= 0 and confidence <= 1),
  attributes jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, entity_type, canonical_name)
);

create table if not exists entity_profiles (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  entity_id uuid not null references entities(id),
  profile_type text not null,
  summary text,
  semantic_summary text,
  attributes jsonb not null default '{}'::jsonb,
  embedding vector(1536),
  generated_from_signal_ids uuid[] not null default '{}',
  created_at timestamptz not null default now()
);

create table if not exists classifications (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  entity_id uuid references entities(id),
  classification_type text not null,
  label text not null,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  method text not null,
  evidence_refs uuid[] not null default '{}',
  created_at timestamptz not null default now()
);

create table if not exists enrichment_records (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  entity_id uuid references entities(id),
  source text not null,
  enrichment_type text not null,
  payload jsonb not null,
  confidence numeric(5,4) not null default 0.5000 check (confidence >= 0 and confidence <= 1),
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Layer 3: Living Knowledge Graph Layer
-- Dynamic graph memory and strategic inference.
-- ---------------------------------------------------------------------------

create table if not exists entity_relationships (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  source_entity_id uuid not null references entities(id),
  target_entity_id uuid not null references entities(id),
  relationship_type text not null,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  inferred boolean not null default false,
  valid_from timestamptz not null default now(),
  valid_to timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  check (source_entity_id <> target_entity_id)
);

create table if not exists relationship_evidence (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  relationship_id uuid not null references entity_relationships(id),
  signal_id uuid references signals(id),
  raw_document_id uuid references raw_documents(id),
  evidence_summary text,
  confidence_contribution numeric(5,4) check (
    confidence_contribution is null or
    (confidence_contribution >= 0 and confidence_contribution <= 1)
  ),
  created_at timestamptz not null default now()
);

create table if not exists graph_snapshots (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  snapshot_type text not null,
  snapshot_uri text,
  node_count integer not null default 0,
  edge_count integer not null default 0,
  graph_embedding vector(1536),
  created_at timestamptz not null default now()
);

create table if not exists graph_evolution (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  entity_id uuid references entities(id),
  relationship_id uuid references entity_relationships(id),
  change_type text not null,
  previous_state jsonb,
  new_state jsonb not null,
  confidence_delta numeric(8,4),
  observed_at timestamptz not null default now()
);

create table if not exists inferred_relationships (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  source_entity_id uuid not null references entities(id),
  target_entity_id uuid not null references entities(id),
  inferred_type text not null,
  inference_method text not null,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  evidence_chain jsonb not null,
  reasoning_ref text,
  status text not null default 'pending_review'
    check (status in ('pending_review', 'accepted', 'rejected', 'superseded')),
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Layer 4: Governance Ledger Layer
-- Append-only governance and audit infrastructure.
-- ---------------------------------------------------------------------------

create table if not exists audit_log (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  actor_type text not null,
  actor_id text not null,
  action text not null,
  resource_type text not null,
  resource_id text not null,
  occurred_at timestamptz not null default now(),
  request_id text,
  ip_address inet,
  user_agent text,
  metadata jsonb not null default '{}'::jsonb,
  integrity_hash text
);

create table if not exists governance_events (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null unique,
  event_type text not null,
  event_version text not null default '1.0',
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  actor_type text not null,
  actor_id text not null,
  actor_display_name text,
  source_service text not null,
  source_request_id text,
  correlation_id uuid not null,
  causation_id uuid,
  occurred_at timestamptz not null,
  received_at timestamptz not null default now(),
  entity_type text not null,
  entity_id text not null,
  policy_context jsonb not null default '{}'::jsonb,
  risk_context jsonb not null default '{}'::jsonb,
  payload jsonb not null default '{}'::jsonb,
  previous_event_hash text,
  integrity_hash text not null
);

create table if not exists policy_evaluations (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  governance_event_id uuid references governance_events(event_id),
  policy_engine text not null default 'opa',
  policy_refs text[] not null default '{}',
  input jsonb not null,
  decision jsonb not null,
  allowed boolean not null,
  requires_human_review boolean not null default false,
  evaluated_at timestamptz not null default now()
);

create table if not exists approvals (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  workflow_id uuid,
  requested_by text not null,
  approver_id text,
  approval_type text not null,
  status text not null default 'requested'
    check (status in ('requested', 'approved', 'denied', 'cancelled', 'expired')),
  reason text,
  requested_at timestamptz not null default now(),
  decided_at timestamptz,
  governance_event_id uuid references governance_events(event_id)
);

create table if not exists workflow_history (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  workflow_id uuid not null,
  workflow_type text not null,
  step_name text not null,
  state text not null,
  actor_id text,
  decision jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now(),
  governance_event_id uuid references governance_events(event_id)
);

create table if not exists ai_decisions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  provider text not null,
  model text not null,
  prompt_hash text not null,
  output_hash text not null,
  citations jsonb not null default '[]'::jsonb,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  reasoning_chain_ref text,
  human_review_state text not null default 'pending_review',
  governance_event_id uuid references governance_events(event_id),
  created_at timestamptz not null default now()
);

create table if not exists human_reviews (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  reviewer_id text not null,
  review_type text not null,
  target_type text not null,
  target_id text not null,
  decision text not null check (decision in ('approved', 'rejected', 'needs_changes', 'escalated')),
  rationale text,
  created_at timestamptz not null default now(),
  governance_event_id uuid references governance_events(event_id)
);

-- ---------------------------------------------------------------------------
-- Layer 5: Cognitive Memory Layer
-- Long-term adaptive intelligence memory.
-- ---------------------------------------------------------------------------

create table if not exists reflections (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  reflection_type text not null,
  subject_type text not null,
  subject_id text not null,
  content text not null,
  evidence_refs jsonb not null default '[]'::jsonb,
  confidence numeric(5,4) not null default 0.5000 check (confidence >= 0 and confidence <= 1),
  created_at timestamptz not null default now()
);

create table if not exists memory_fragments (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  memory_type text not null,
  content text not null,
  embedding vector(1536),
  source_refs jsonb not null default '[]'::jsonb,
  retention_policy text not null default 'standard',
  created_at timestamptz not null default now()
);

create table if not exists strategic_patterns (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  pattern_type text not null,
  description text not null,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  supporting_memory_ids uuid[] not null default '{}',
  created_at timestamptz not null default now(),
  last_observed_at timestamptz
);

create table if not exists user_preferences (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  subject_id text not null,
  preference_type text not null,
  value jsonb not null,
  confidence numeric(5,4) not null default 0.5000 check (confidence >= 0 and confidence <= 1),
  source text not null default 'explicit',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, subject_id, preference_type)
);

create table if not exists simulation_results (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  simulation_type text not null,
  input_hash text not null,
  result jsonb not null,
  confidence numeric(5,4) not null default 0.5000 check (confidence >= 0 and confidence <= 1),
  created_at timestamptz not null default now()
);

create table if not exists execution_feedback (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  execution_type text not null,
  target_type text not null,
  target_id text not null,
  outcome text not null,
  feedback jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Layer 6: Operational Runtime Layer
-- Live orchestration state.
-- ---------------------------------------------------------------------------

create table if not exists runtime_sessions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  session_type text not null,
  actor_id text not null,
  status text not null default 'active'
    check (status in ('active', 'paused', 'completed', 'failed', 'cancelled')),
  state jsonb not null default '{}'::jsonb,
  started_at timestamptz not null default now(),
  ended_at timestamptz
);

create table if not exists active_tasks (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  runtime_session_id uuid references runtime_sessions(id),
  task_type text not null,
  status text not null default 'queued'
    check (status in ('queued', 'running', 'waiting_for_review', 'completed', 'failed', 'cancelled')),
  assigned_to text,
  payload jsonb not null default '{}'::jsonb,
  due_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists orchestration_state (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  orchestration_key text not null,
  state jsonb not null,
  version integer not null default 1,
  updated_at timestamptz not null default now(),
  unique (tenant_id, orchestration_key)
);

create table if not exists inspector_runs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  inspector_name text not null,
  objective text not null,
  status text not null default 'started'
    check (status in ('started', 'completed', 'failed', 'cancelled', 'waiting_for_review')),
  confidence_threshold numeric(5,4) not null default 0.7500,
  findings jsonb not null default '[]'::jsonb,
  governance_event_id uuid references governance_events(event_id),
  started_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists event_queue (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  event_type text not null,
  payload jsonb not null,
  status text not null default 'queued'
    check (status in ('queued', 'processing', 'processed', 'failed', 'dead_letter')),
  attempts integer not null default 0,
  available_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  processed_at timestamptz
);

-- ---------------------------------------------------------------------------
-- Guardrails, indexes, and row-level security foundation
-- ---------------------------------------------------------------------------

create or replace function prevent_update_delete()
returns trigger
language plpgsql
as $$
begin
  raise exception 'append-only table % does not allow %', tg_table_name, tg_op;
end;
$$;

create trigger signals_append_only_update
before update or delete on signals
for each row execute function prevent_update_delete();

create trigger raw_documents_append_only_update
before update or delete on raw_documents
for each row execute function prevent_update_delete();

create trigger audit_log_append_only_update
before update or delete on audit_log
for each row execute function prevent_update_delete();

create trigger governance_events_append_only_update
before update or delete on governance_events
for each row execute function prevent_update_delete();

create index if not exists idx_signals_tenant_observed
  on signals (tenant_id, observed_at desc);

create index if not exists idx_entities_tenant_type_name
  on entities (tenant_id, entity_type, canonical_name);

create index if not exists idx_entity_relationships_tenant_source
  on entity_relationships (tenant_id, source_entity_id);

create index if not exists idx_entity_relationships_tenant_target
  on entity_relationships (tenant_id, target_entity_id);

create index if not exists idx_governance_events_tenant_time
  on governance_events (tenant_id, occurred_at desc);

create index if not exists idx_governance_events_correlation
  on governance_events (tenant_id, correlation_id);

create index if not exists idx_active_tasks_tenant_status
  on active_tasks (tenant_id, status, due_at);

alter table organizations enable row level security;
alter table tenants enable row level security;
alter table tenant_memberships enable row level security;
alter table signal_sources enable row level security;
alter table ingestion_runs enable row level security;
alter table crawl_jobs enable row level security;
alter table raw_documents enable row level security;
alter table signals enable row level security;
alter table entities enable row level security;
alter table entity_profiles enable row level security;
alter table classifications enable row level security;
alter table enrichment_records enable row level security;
alter table entity_relationships enable row level security;
alter table relationship_evidence enable row level security;
alter table graph_snapshots enable row level security;
alter table graph_evolution enable row level security;
alter table inferred_relationships enable row level security;
alter table audit_log enable row level security;
alter table governance_events enable row level security;
alter table policy_evaluations enable row level security;
alter table approvals enable row level security;
alter table workflow_history enable row level security;
alter table ai_decisions enable row level security;
alter table human_reviews enable row level security;
alter table reflections enable row level security;
alter table memory_fragments enable row level security;
alter table strategic_patterns enable row level security;
alter table user_preferences enable row level security;
alter table simulation_results enable row level security;
alter table execution_feedback enable row level security;
alter table runtime_sessions enable row level security;
alter table active_tasks enable row level security;
alter table orchestration_state enable row level security;
alter table inspector_runs enable row level security;
alter table event_queue enable row level security;

comment on schema noetfield is 'Noetfield governed intelligence memory and runtime schema.';
comment on table signals is 'Layer 1 immutable raw signal memory.';
comment on table entities is 'Layer 2 normalized intelligence entities.';
comment on table entity_relationships is 'Layer 3 living knowledge graph edges.';
comment on table governance_events is 'Layer 4 append-only Trust Ledger event stream.';
comment on table reflections is 'Layer 5 cognitive memory reflection store.';
comment on table runtime_sessions is 'Layer 6 live orchestration runtime state.';
