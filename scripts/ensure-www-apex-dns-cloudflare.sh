#!/usr/bin/env bash
# Point apex noetfield.com at Cloudflare Pages (301 → www) — fixes stale Vercel apex 404.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
ZONE="${CF_NOETFIELD_ZONE_ID:-456aeba6b1a37d1fadbf6443cb929468}"
PROJECT="${CF_PAGES_PROJECT:-noetfield-www}"
APEX="${NF_WWW_APEX_DOMAIN:-noetfield.com}"
WWW="${NF_WWW_LIVE_DOMAIN:-www.noetfield.com}"

log() { printf '[ensure-www-apex-dns] %s\n' "$*" >&2; }

read_vault_token() {
  # shellcheck disable=SC1090
  [[ -f "$VAULT" ]] && source "$VAULT" 2>/dev/null || true
  printf '%s' "${CF_NOETFIELD_API_TOKEN:-${CF_API_TOKEN:-}}"
}

pages_target() {
  if [[ -n "${CF_PAGES_CNAME_TARGET:-}" ]]; then
    printf '%s' "$CF_PAGES_CNAME_TARGET"
    return 0
  fi
  local sub
  sub="$(npx wrangler pages deployment list --project-name "$PROJECT" --environment production 2>/dev/null | grep -Eo '[a-z0-9-]+\.pages\.dev' | head -1 || true)"
  if [[ -n "$sub" ]]; then
    printf '%s' "$sub"
    return 0
  fi
  printf '%s' "${PROJECT}.pages.dev"
}

token="$(read_vault_token)"
TARGET="${CF_PAGES_CNAME_TARGET:-$(pages_target)}"
if [[ -z "$TARGET" ]]; then
  log "FAIL: could not resolve Pages CNAME target for ${PROJECT}"
  exit 2
fi

log "attach apex + www on Pages project ${PROJECT}…"
ACCT="${CF_ACCOUNT_ID:-0d0b967b77e2e5535455d39ff3dae72c}"
WRANGLER_CFG="${HOME}/.wrangler/config/default.toml"
OAUTH_TOKEN=""
if [[ -f "$WRANGLER_CFG" ]]; then
  OAUTH_TOKEN="$(python3 -c "import re,pathlib; t=pathlib.Path('${WRANGLER_CFG}').read_text(); m=re.search(r'oauth_token = \\\"([^\\\"]+)\\\"', t); print(m.group(1) if m else '')" 2>/dev/null || true)"
fi
if [[ -n "$OAUTH_TOKEN" ]]; then
  for dom in "$WWW" "$APEX"; do
    resp="$(curl -sS -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCT}/pages/projects/${PROJECT}/domains" \
      -H "Authorization: Bearer ${OAUTH_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"${dom}\"}" 2>/dev/null || true)"
    python3 -c "import json,sys; d=json.load(sys.stdin); print('pages_domain',sys.argv[1],d.get('success'), d.get('errors',[{}])[0].get('message','') if not d.get('success') else 'ok')" "$dom" <<<"$resp" 2>/dev/null || log "pages domain ${dom} attach skipped"
  done
else
  log "WARN: wrangler oauth missing — add ${APEX} in Cloudflare Pages custom domains"
fi

if [[ -z "$token" ]]; then
  log "WARN: CF_NOETFIELD_API_TOKEN missing — attach domains only; set apex DNS manually"
  exit 0
fi

log "patch apex DNS (@) → ${TARGET} (proxied CNAME flatten)…"
apex_id="$(curl -sS -G "https://api.cloudflare.com/client/v4/zones/${ZONE}/dns_records" \
  -H "Authorization: Bearer ${token}" \
  --data-urlencode "type=A" \
  --data-urlencode "name=${APEX}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('result',[]):
    if r.get('name') in ('${APEX}','@'):
        print(r.get('id',''))
        break
" 2>/dev/null || true)"

body="$(python3 -c "import json; print(json.dumps({'type':'CNAME','name':'${APEX}','content':'${TARGET}','ttl':1,'proxied':True}))")"

if [[ -n "$apex_id" ]]; then
  curl -sS -X DELETE "https://api.cloudflare.com/client/v4/zones/${ZONE}/dns_records/${apex_id}" \
    -H "Authorization: Bearer ${token}" >/dev/null || true
fi
resp="$(curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE}/dns_records" \
  -H "Authorization: Bearer ${token}" \
  -H "Content-Type: application/json" \
  -d "$body")"

python3 -c "import json,sys; d=json.load(sys.stdin); print('apex_dns',d.get('success')); sys.exit(0 if d.get('success') else 1)" <<<"$resp"

log "waiting for apex…"
for _ in $(seq 1 18); do
  code="$(curl -sS -o /dev/null -w '%{http_code}' -L "https://${APEX}/" 2>/dev/null || echo 000)"
  if [[ "$code" != "404" && "$code" != "000" ]]; then
    log "apex https://${APEX}/ → HTTP ${code}"
    exit 0
  fi
  sleep 5
done

log "WARN: apex still not responding — DNS may need manual confirm in Cloudflare dashboard"
exit 0
