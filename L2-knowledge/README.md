# L2 Knowledge Architecture

## Layout

| Path | Purpose |
|------|---------|
| `strategy/full/` | Complete mirror of all uploaded batches |
| `strategy/noetfield/` | Production runtime + GTM knowledge only |
| `strategy/reference-products/` | POSA, AIE, SLF, PAIOS, theory — **must not drive Noetfield runtime** |
| `perplexity-ai-native-development-guidelines.md` | Operator/dev guidelines (L2 root) |

## Archived tooling (do not wire to Noetfield runtime)

- **n8n** — workflow automation experiments (archived)
- **Ollama** — local model dev only in docker-compose; not production authority
- **PAIOS** — separate personal AI OS lineage; PAIOS-only reference

## Supremacy

`NORTH_STAR.md` and GCIP v4 override this tree on conflict.
