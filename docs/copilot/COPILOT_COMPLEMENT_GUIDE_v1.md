# Copilot complement guide (client-safe)

**Noetfield lane:** Complement — registry vs receipt  
**Use:** Copilot hub copy + partner conversations. Not a platform partnership claim.

---

## Division of labour

| Layer | Typical owner | Noetfield role |
|-------|---------------|----------------|
| Agent registry / fleet | Workspace platform | **Observe** — we do not replace registry |
| Data classification / DLP | Compliance metadata layer | **Index metadata** — no content custody |
| Tenant policy configuration | MSP / CSP operations | **Pre-exec evaluate** — allow/deny before workspace acts |
| Audit receipt | Noetfield | **TLE v1** — signed go/no-go + export |

## Complement story (locked)

> **Registry tells you what exists. Classification tells you what data is sensitive. Noetfield tells you what was permitted before execution — with a receipt your board can cite.**

## Integration pattern

1. Intent + context → `POST /evaluate`  
2. Decision + RID → compliance log  
3. Optional connector sync → compliance and identity metadata index  
4. Export → board PDF + procurement ZIP  

## Related

- [SME_BUYER_JOURNEY.md](./SME_BUYER_JOURNEY.md)
- [PROCUREMENT_ONE_PAGER.md](./PROCUREMENT_ONE_PAGER.md)
