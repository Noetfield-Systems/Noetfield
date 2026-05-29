-- Source-of-truth registry and document inventory.
-- PostgreSQL is the governance authority for source documents and active rules.

set search_path = noetfield, public;

create table if not exists source_document_batches (
  id uuid primary key default gen_random_uuid(),
  batch_key text not null unique,
  source_folder text not null,
  received_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists source_documents (
  id uuid primary key default gen_random_uuid(),
  batch_id uuid references source_document_batches(id),
  document_key text not null unique,
  title text not null,
  domain text not null,
  work_package text,
  version_label text,
  source_path text not null,
  content_sha256 text not null,
  classification text not null,
  status text not null,
  supersedes text[] not null default '{}',
  superseded_by text,
  metadata jsonb not null default '{}'::jsonb,
  registered_at timestamptz not null default now()
);

create table if not exists source_of_truth_registry (
  id uuid primary key default gen_random_uuid(),
  registry_version text not null,
  domain text not null,
  active_document_key text not null references source_documents(document_key),
  active_version text,
  decision text not null,
  rationale text not null,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  decided_at timestamptz not null default now(),
  unique (registry_version, domain)
);

create table if not exists active_rule_candidates (
  id uuid primary key default gen_random_uuid(),
  registry_version text not null,
  rule_key text not null,
  domain text not null,
  source_document_key text not null references source_documents(document_key),
  activation_status text not null
    check (activation_status in ('active_design_rule', 'candidate_requires_formalization', 'reference_only')),
  rule_type text not null,
  summary text not null,
  implementation_target text,
  metadata jsonb not null default '{}'::jsonb,
  registered_at timestamptz not null default now(),
  unique (registry_version, rule_key)
);

alter table source_document_batches enable row level security;
alter table source_documents enable row level security;
alter table source_of_truth_registry enable row level security;
alter table active_rule_candidates enable row level security;

create index if not exists idx_source_documents_domain
  on source_documents (domain, classification);

create index if not exists idx_source_of_truth_registry_domain
  on source_of_truth_registry (domain, decided_at desc);

create index if not exists idx_active_rule_candidates_domain
  on active_rule_candidates (domain, activation_status);

comment on table source_documents is 'Uploaded source documents with content hashes and provenance.';
comment on table source_of_truth_registry is 'Active source-of-truth decisions per domain.';
comment on table active_rule_candidates is 'Design rules extracted from active source documents.';
