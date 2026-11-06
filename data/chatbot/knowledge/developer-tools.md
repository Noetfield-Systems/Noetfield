# Developer tools — GEL and noetfield-gate

## Public developer entry point

- GEL product page: https://www.noetfield.com/gel/
- Public API documentation: https://www.noetfield.com/openapi.json
- Hosted API base: https://api.noetfield.com
- Free developer sandbox: https://www.noetfield.com/start/

## noetfield-gate

The public Python package is named `noetfield-gate`.

```bash
pip install noetfield-gate
noetfield gate
noetfield decide --sample
```

The local gate command produces a local decision report. Hosted API calls require a provisioned API key; never place API keys in browser code or commit them to source control.

## Environment

| Variable | Purpose |
|---|---|
| `NOETFIELD_API_URL` | GEL API base URL; defaults to `https://api.noetfield.com` |
| `NOETFIELD_API_KEY` | Server-side API key for hosted decision requests |
| `NOETFIELD_ROOT` | Optional repository root override |

## Keep the product boundary clear

GEL is the Governance Execution Layer behind governed workflows. It is not a payment gateway, custody service, generic chatbot catalog, or an exchange.
