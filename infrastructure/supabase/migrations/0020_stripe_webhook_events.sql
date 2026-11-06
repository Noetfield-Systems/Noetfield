-- Durable Stripe webhook event receipts for duplicate-safe processing.
create schema if not exists noetfield;

create table if not exists noetfield.stripe_webhook_events (
  stripe_event_id text primary key,
  event_type text not null,
  stripe_object_id text not null default '',
  status text not null check (status in ('processing', 'processed', 'failed')),
  attempts integer not null default 1 check (attempts > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  processed_at timestamptz,
  last_error text
);

create index if not exists idx_stripe_webhook_events_status_updated
  on noetfield.stripe_webhook_events (status, updated_at);
