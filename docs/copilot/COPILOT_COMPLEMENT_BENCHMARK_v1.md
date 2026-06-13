# Copilot complement benchmark (internal)

**Benchmark set:** Microsoft Control System · Purview · Inforcer  
**Noetfield lane:** Complement — registry vs receipt  
**Use:** Copilot hub copy + partner conversations. Not a Microsoft partnership claim.

---

## Division of labour

| Layer | Owner | Noetfield role |
|-------|-------|----------------|
| Agent registry / fleet | Microsoft Agent 365 | **Observe** — we do not replace registry |
| Data classification / DLP | Purview | **Index metadata** — no content custody |
| Tenant policy configuration | Inforcer-style MSP tools | **Pre-exec evaluate** — allow/deny before M365 acts |
| Audit receipt | Noetfield | **TLE v1** — signed go/no-go + export |

## Complement story (locked)

> **Registry tells you what exists. Purview tells you what data is sensitive. Noetfield tells you what was permitted before execution — with a receipt your board can cite.**

## Integration pattern

1. Intent + context → `POST /evaluate`  
2. Decision + RID → compliance log  
3. Optional connector sync → Purview / Entra metadata index  
4. Export → board PDF + procurement ZIP  

## Related

- [COPILOT_COMPLEMENT_BENCHMARK_v1.md](./COPILOT_COMPLEMENT_BENCHMARK_v1.md) — same file path for www link  
- [SME_BUYER_JOURNEY.md](../copilot/SME_BUYER_JOURNEY.md)
