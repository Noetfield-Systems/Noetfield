-- Durable Stripe webhook event ledger for Live commercial licensing notifications.
-- The event id primary key prevents duplicate notifications when Stripe retries delivery.

set search_path = noetfield, public;

create table if not exists stripe_webhook_events (
  event_id text primary key,
  event_type text not null,
  livemode boolean not null,
  payload_sha256 text not null,
  status text not null default 'received'
    check (status in ('received', 'processing', 'processed', 'failed')),
  attempts integer not null default 0 check (attempts >= 0),
  last_error text,
  received_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  processed_at timestamptz
);

create index if not exists idx_stripe_webhook_events_status_updated
  on stripe_webhook_events (status, updated_at desc);

create index if not exists idx_stripe_webhook_events_type_received
  on stripe_webhook_events (event_type, received_at desc);
