# Noetfield Systems
Infrastructure for AI trust and stewardship

## Current law stack (read first)

**Visible entry:** [docs/LAWS/README.md](docs/LAWS/README.md) · **Latest stack:** [docs/LAWS/CURRENT_STACK_v2026.md](docs/LAWS/CURRENT_STACK_v2026.md) · **L0 pointer:** [L0-law/CURRENT.md](L0-law/CURRENT.md)

```bash
make verify-law-stack    # anti-fragmentation / anti-drift
make sync-derived-docs   # regenerate L2 + All-Documents mirrors
```

Old constitutional versions stay in batch folders — indexed in [docs/SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md](docs/SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md), not deleted (registry path integrity).

## Platform blueprint

See [PLATFORM_BLUEPRINT.md](PLATFORM_BLUEPRINT.md) for the architecture
constitution guiding Noetfield's transition from a static vision and branding
site into an enterprise AI governance operating system.

## Noetfield v3.1 executable foundation

The repository now includes the initial monorepo foundation for the Noetfield
Autonomous Governed Intelligence Nervous System:

- `apps/` contains Next.js app shells for public web, platform, and admin.
- `services/` contains modular FastAPI/Python service boundaries.
- `packages/` contains shared typed contracts, schemas, config, SDK, prompts,
  and shared utilities.
- `infrastructure/` contains Docker, Supabase/PostgreSQL, monitoring, and
  Terraform scaffolding.
- `docs/SOURCE_OF_TRUTH/` records the v3.1 constitutional source layer.

Start with [docs/DEVELOPER_BOOTSTRAP.md](docs/DEVELOPER_BOOTSTRAP.md).
