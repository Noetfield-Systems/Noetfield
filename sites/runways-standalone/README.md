# Standalone Runways product site (Cloudflare Pages)

Independent sell surface for **Runways** — not the corporate Noetfield mega-site.

| Surface | URL |
|---|---|
| Product | `https://noetfield-runways.pages.dev/` |
| Implement playbook | `https://noetfield-runways.pages.dev/implement/` |
| Corporate mirror | `https://www.noetfield.com/runways/` |

## Why standalone

- Sell Runways as its own product SKU.
- Other brands (Trustfield, SourceA, SourceB) copy this folder + Pages project; they do **not** fork the Motor.
- Motor remains `NOETFIELD-RUNWAY` (`POST /v1/jobs`).

## Deploy

```bash
export CLOUDFLARE_API_TOKEN=…
export RUNWAY_RUNTIME_API_SECRET=…   # optional but required for live dispatch
bash scripts/deploy.sh
```

Or GitHub Action: `Deploy Runways Standalone`.

## Secrets

- `RUNWAY_RUNTIME_API_SECRET`
- `RUNWAY_RUNTIME_BASE_URL` (staging Worker by default)
- `RUNWAY_RUNTIME_KEY_ID` (`staging-proof`)

Sync from NOETFIELD-RUNWAY workflow `Sync www Runway dispatch secret` (also targets this project).
