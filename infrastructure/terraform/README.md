# Terraform Scaffolding

This directory is reserved for cloud infrastructure modules.

Initial modules should provision:

- managed PostgreSQL or Supabase project
- Redis-compatible cache
- object storage for evidence
- KMS or cloud key vault
- secrets manager
- container runtime
- private networking
- observability sinks

Do not encode production secrets in Terraform variables. Use managed secret
stores and environment-specific workspaces.
