# Telegram bot (Noetfield assistant)

## Security (required)

- **Never** commit `TELEGRAM_BOT_TOKEN` to git or put it in frontend JavaScript.
- If the token was shared in chat or email, **revoke it** via [@BotFather](https://t.me/BotFather) (`/revoke`) and issue a new token.
- Store only in server environment variables or your secrets manager.

## Architecture

| Component | Role |
|-----------|------|
| Telegram user | Messages your bot |
| `POST /api/telegram/webhook` | FastAPI receives updates (HTTPS required) |
| `handle_telegram_update` | Same FAQ knowledge + OpenRouter/Gemini as website chat |
| `TELEGRAM_BOT_TOKEN` | Server env only |

## Environment

```bash
TELEGRAM_BOT_TOKEN=          # from @BotFather — server only
TELEGRAM_WEBHOOK_BASE_URL=https://platform.noetfield.com
TELEGRAM_WEBHOOK_SECRET=     # random string; sent as X-Telegram-Bot-Api-Secret-Token
TELEGRAM_BOT_ENABLED=true

# LLM (same as website chat)
OPENROUTER_API_KEY=
PUBLIC_CHAT_PROVIDER=auto
```

## Register webhook (production)

After the API is reachable on HTTPS:

```bash
export TELEGRAM_WEBHOOK_SECRET="your-random-secret"
curl -X POST "https://platform.noetfield.com/api/telegram/register-webhook" \
  -H "X-Admin-Secret: your-random-secret"
```

Or use the script:

```bash
TELEGRAM_BOT_TOKEN=... TELEGRAM_WEBHOOK_BASE_URL=https://platform.noetfield.com \
  TELEGRAM_WEBHOOK_SECRET=... python3 scripts/register_telegram_webhook.py
```

## Health checks

- `GET /api/telegram/health` — includes live `getWebhookInfo`, `ready`, and a plain-English `hint`
- `GET /api/ecosystem/health` — website chat + Telegram + providers

On the platform server:

```bash
curl -sS https://platform.noetfield.com/api/telegram/health | python3 -m json.tool
```

Or locally:

```bash
PYTHONPATH=packages/types:packages/config:services/governance \
  TELEGRAM_BOT_TOKEN=... TELEGRAM_WEBHOOK_BASE_URL=https://platform.noetfield.com \
  python3 scripts/diagnose_telegram_bot.py
```

## Troubleshooting (bot not responding)

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| No reply at all | Webhook not registered or wrong host | API must run on **platform** (`make api-v3`, port 8001), not static www |
| No reply at all | `TELEGRAM_BOT_TOKEN` missing on server | Set env, restart API, `GET /api/telegram/health` → `configured: true` |
| No reply at all | Webhook secret mismatch | If `TELEGRAM_WEBHOOK_SECRET` is set, re-run `register-webhook` with the same value; Telegram sends `X-Telegram-Bot-Api-Secret-Token` |
| `/start` works, questions fail | No `OPENROUTER_API_KEY` / `GEMINI_API_KEY` | Add LLM key; health shows `llm_configured: false` |
| Health shows `last_error_message` | TLS/firewall/DNS | Ensure `https://platform.noetfield.com/api/telegram/webhook` is reachable from the public internet |
| Token was pasted in chat | Revoked token | `/revoke` in @BotFather, new token in env only, re-register webhook |

The webhook returns HTTP 200 immediately and processes messages in the background so slow LLM replies do not cause Telegram delivery failures.

## Commands (registered in BotFather menu)

| Command | Description |
|---------|-------------|
| `/start` | Welcome + inline menu |
| `/help` | Usage guide |
| `/offerings` | All three SKUs |
| `/trustbrief` | Trust Brief $10,000 |
| `/copilot` | Copilot Governance Pack |
| `/pilot` | Bank Pilot (read-only) |
| `/intake` | Request Governance Brief |
| `/human` | operations@noetfield.com |
| `/reset` | Clear conversation memory |

Free-text questions use the same LLM + FAQ knowledge as the website, with **typing indicator** and **session memory** (last 8 turns).

**Inline buttons:** Trust Brief, Copilot, Bank Pilot, Request Brief (URL), FAQ.
