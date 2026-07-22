-- Pilot API keys (hashed at rest; plaintext returned only on create).

set search_path = noetfield, public;

create table if not exists pilot_api_keys (
  key_id uuid primary key default gen_random_uuid(),
  key_prefix text not null,
  key_hash text not null unique,
  label text not null,
  tenant_id uuid,
  scopes text[] not null default '{}',
  created_at timestamptz not null default now(),
  revoked_at timestamptz,
  created_by text not null default 'system'
);

create index if not exists pilot_api_keys_active_idx
  on pilot_api_keys (key_prefix) where revoked_at is null;
