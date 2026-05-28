# Supabase Foundation

The v3.1 schema is defined in
`migrations/0001_noetfield_v3_1_foundation.sql`.

The schema is intentionally layered:

1. Raw Signal Layer
2. Normalized Intelligence Layer
3. Living Knowledge Graph Layer
4. Governance Ledger Layer
5. Cognitive Memory Layer
6. Operational Runtime Layer

Raw signal and governance ledger tables are append-only through database
triggers. Row-level security is enabled as a foundation for tenant isolation;
tenant-specific policies should be added with the authentication strategy.
