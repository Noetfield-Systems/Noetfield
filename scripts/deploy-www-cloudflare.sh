#!/usr/bin/env bash
# Production deploy www.noetfield.com → Cloudflare Pages (noetfield-www).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT="${CF_PAGES_PROJECT:-noetfield-www}"
BRANCH="${CF_PAGES_BRANCH:-main}"
CANONICAL="${NF_WWW_CANONICAL_URL:-https://www.noetfield.com}"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
ZONE="${CF_NOETFIELD_ZONE_ID:-456aeba6b1a37d1fadbf6443cb929468}"
ACCOUNT="${CLOUDFLARE_ACCOUNT_ID:-0d0b967b77e2e5535455d39ff3dae72c}"
PAGES_ALIAS="https://${PROJECT}.pages.dev"
WRANGLER_VERSION="${CF_WRANGLER_VERSION:-4.103.0}"
WRANGLER=(npx --yes "wrangler@${WRANGLER_VERSION}")
DEPLOY_RECEIPT_PATH="${CF_DEPLOY_RECEIPT_PATH:-/tmp/noetfield-www-deploy-receipt.json}"
ARTIFACT_MANIFEST="${ROOT}/tmp/noetfield-www/public-artifact-manifest.json"
PURGE_RESPONSE='{"status":"not_requested"}'
PROXY_DEPLOY_OUT=""
PROXY_HTTP_STATUS=""
PROXY_IDENTITY=""
PROXY_RELEASE=""
PROXY_BODY_SHA256=""

log() { printf '[deploy-www-cloudflare] %s\n' "$*"; }

read_vault() {
  local key="$1"
  if [[ ! -f "$VAULT" ]]; then return 1; fi
  grep -E "^${key}=" "$VAULT" | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//' || true
}

provider_token() {
  local token
  token="${CLOUDFLARE_API_TOKEN:-}"
  if [[ -n "$token" ]]; then
    printf '%s' "$token"
    return 0
  fi
  if token="$("${WRANGLER[@]}" auth token --json 2>/dev/null | python3 -c '
import json, sys
value = json.load(sys.stdin).get("token", "")
if not value:
    raise SystemExit(1)
print(value, end="")
')"; then
    printf '%s' "$token"
    return 0
  fi
  read_vault CF_NOETFIELD_API_TOKEN || read_vault CF_API_TOKEN
}

cloudflare_api_get() {
  local path="$1"
  curl -sS --fail-with-body \
    -H "Authorization: Bearer ${CF_PROVIDER_TOKEN}" \
    "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT}/${path}"
}

assert_clean_release_source() {
  local phase="$1"
  local tracked
  tracked="$(git status --porcelain --untracked-files=no)"
  if [[ -n "$tracked" ]]; then
    log "FAIL: tracked worktree changes detected ${phase}; commit the exact release first"
    printf '%s\n' "$tracked" >&2
    return 1
  fi
}

sync_pages_secrets() {
  local key value
  for key in RESEND_API_KEY INTAKE_EMAIL_FROM INTAKE_EMAIL_TO OPENROUTER_API_KEY TELEGRAM_NOETFIELD_OPS_BOT_TOKEN TELEGRAM_OPS_CHAT_ID; do
    value="$(read_vault "$key" || true)"
    if [[ -n "$value" ]]; then
      log "pages secret ${key}"
      printf '%s' "$value" | "${WRANGLER[@]}" pages secret put "$key" --project-name "$PROJECT" 2>/dev/null || \
        log "WARN: could not set secret ${key}"
    fi
  done
}

ensure_project() {
  local project branch
  project="$(cloudflare_api_get "pages/projects/${PROJECT}")"
  branch="$(printf '%s' "$project" | python3 scripts/resolve-cf-pages-release.py project \
    --project-name "$PROJECT" --expected-branch "$BRANCH")"
  log "canonical project confirmed: ${PROJECT} (production branch=${branch})"
}

resolve_deployment() {
  local expected_sha="$1"
  local attempt deployments row
  for attempt in $(seq 1 12); do
    deployments="$(cloudflare_api_get "pages/projects/${PROJECT}/deployments?env=production")"
    if row="$(printf '%s' "$deployments" | python3 scripts/resolve-cf-pages-release.py deployment \
        --project-name "$PROJECT" --expected-branch "$BRANCH" \
        --expected-sha "$expected_sha")"; then
      printf '%s' "$row"
      return 0
    fi
    log "exact deployment metadata not visible yet — retry ${attempt}/12" >&2
    sleep 2
  done
  return 1
}

wait_for_service_health() {
  local base="$1"
  local expected_sha="$2"
  local attempt code service live_sha body_file
  service=""
  live_sha=""
  body_file="$(mktemp "${TMPDIR:-/tmp}/nf-www-health.XXXXXX")"
  for attempt in $(seq 1 12); do
    service=""
    live_sha=""
    if ! code="$(curl -sS -o "$body_file" -w '%{http_code}' \
      "${base%/}/api/health?nf_release=${expected_sha}&nf_cachebust=${attempt}" \
      2>/dev/null)"; then
      code="000"
    fi
    read -r service live_sha < <(python3 - "$body_file" <<'PY' 2>/dev/null || true
import json, sys
body = json.load(open(sys.argv[1], encoding="utf-8"))
print(str(body.get("service") or ""), str(body.get("git_sha") or ""))
PY
) || true
    if [[ "$code" == "200" && "$service" == "noetfield-www" ]]; then
      rm -f -- "$body_file"
      log "${base} service health ready sha=${live_sha:0:12} (${attempt})"
      return 0
    fi
    log "${base} health=${code} service=${service:-missing} — retry ${attempt}/12"
    sleep 5
  done
  rm -f -- "$body_file"
  return 1
}

verify_release_surface() {
  local base="$1"
  shift
  local attempt
  for attempt in $(seq 1 12); do
    if python3 scripts/nf_post_deploy_verify.py --www-base "$base" "$@"; then
      log "${base} full surface verification ready (${attempt})"
      return 0
    fi
    log "${base} full surface verification pending (${attempt}/12)"
    sleep 2
  done
  return 1
}

sha256_url() {
  local base="$1"
  local path="$2"
  local expected_sha="$3"
  local body_file hash
  body_file="$(mktemp "${TMPDIR:-/tmp}/nf-www-content.XXXXXX")"
  if ! curl -sS --fail "${base%/}${path}?nf_release=${expected_sha}" -o "$body_file"; then
    rm -f -- "$body_file"
    return 1
  fi
  if ! hash="$(shasum -a 256 "$body_file" | awk '{print $1}')"; then
    rm -f -- "$body_file"
    return 1
  fi
  rm -f -- "$body_file"
  printf '%s' "$hash"
}

compare_release_content() {
  local expected_base="$1"
  local observed_base="$2"
  local expected_sha="$3"
  local path attempt expected_hash observed_hash matched
  for path in / /assets/noetfield-corporate-v1.css /noetfield-favicon-512.png; do
    expected_hash=""
    observed_hash=""
    matched=0
    for attempt in $(seq 1 12); do
      expected_hash=""
      observed_hash=""
      if expected_hash="$(sha256_url "$expected_base" "$path" "$expected_sha")" &&
         observed_hash="$(sha256_url "$observed_base" "$path" "$expected_sha")" &&
         [[ -n "$expected_hash" && "$expected_hash" == "$observed_hash" ]]; then
        matched=1
        break
      fi
      log "release content pending path=${path} expected=${expected_hash:-unavailable} observed=${observed_hash:-unavailable} (${attempt}/12)"
      sleep 2
    done
    if [[ "$matched" != "1" ]]; then
      log "FAIL: release content mismatch path=${path} expected=${expected_hash:-missing} observed=${observed_hash:-missing}"
      return 1
    fi
    log "release content match path=${path} sha256=${observed_hash}"
  done
}

confirm_proxy_pin() {
  local expected_sha="$1"
  local attempt headers_file body_file code identity service
  service=""
  headers_file="$(mktemp "${TMPDIR:-/tmp}/nf-www-headers.XXXXXX")"
  body_file="$(mktemp "${TMPDIR:-/tmp}/nf-www-body.XXXXXX")"
  for attempt in $(seq 1 12); do
    : > "$headers_file"
    PROXY_IDENTITY=""
    PROXY_RELEASE=""
    PROXY_BODY_SHA256=""
    service=""
    if ! code="$(curl -sS -D "$headers_file" -o "$body_file" -w '%{http_code}' \
      "${CANONICAL%/}/api/health?nf_release=${expected_sha}&nf_cachebust=${attempt}" \
      2>/dev/null)"; then
      code="000"
    fi
    identity="$(python3 - "$headers_file" "$body_file" <<'PY' 2>/dev/null || true
import hashlib, json, sys
headers = {}
for line in open(sys.argv[1], encoding="iso-8859-1"):
    if ":" in line:
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
body_bytes = open(sys.argv[2], "rb").read()
try:
    body = json.loads(body_bytes)
except (json.JSONDecodeError, UnicodeDecodeError):
    body = {}
print(
    headers.get("x-noetfield-proxy", ""),
    headers.get("x-noetfield-release", ""),
    body.get("service", ""),
    hashlib.sha256(body_bytes).hexdigest(),
    sep="\t",
)
PY
)"
    IFS=$'\t' read -r PROXY_IDENTITY PROXY_RELEASE service PROXY_BODY_SHA256 <<< "$identity" || true
    PROXY_HTTP_STATUS="$code"
    if [[ "$code" == "200" && "$PROXY_IDENTITY" == "cf-www-proxy" && \
          "$PROXY_RELEASE" == "$expected_sha" && "$service" == "noetfield-www" ]]; then
      rm -f -- "$headers_file" "$body_file"
      log "canonical proxy pin confirmed release=${expected_sha:0:12} (${attempt})"
      return 0
    fi
    log "canonical proxy pin pending status=${code} proxy=${PROXY_IDENTITY:-missing} release=${PROXY_RELEASE:0:12} (${attempt}/12)"
    sleep 5
  done
  rm -f -- "$headers_file" "$body_file"
  return 1
}

purge_public_host_cache() {
  local response
  if [[ -z "$CF_PROVIDER_TOKEN" ]]; then
    log "FAIL: cache purge requested but no Cloudflare API token is available"
    return 1
  fi
  log "purging scoped host cache: noetfield.com, www.noetfield.com"
  response="$(curl -sS --fail-with-body -X POST \
      "https://api.cloudflare.com/client/v4/zones/${ZONE}/purge_cache" \
      -H "Authorization: Bearer ${CF_PROVIDER_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"hosts":["noetfield.com","www.noetfield.com"]}')"
  PURGE_RESPONSE="$response"
  printf '%s' "$response" | python3 -c '
import json, sys
body = json.load(sys.stdin)
if body.get("success") is not True:
    raise SystemExit("Cloudflare scoped cache purge failed")
print("[deploy-www-cloudflare] scoped cache purge accepted")
'
}

write_deploy_receipt() {
  local manifest_hash
  manifest_hash="$(shasum -a 256 "$ARTIFACT_MANIFEST" | awk '{print $1}')"
  NF_RECEIPT_PATH="$DEPLOY_RECEIPT_PATH" \
  NF_RECEIPT_EXPECTED_SHA="$EXPECTED_SHA" \
  NF_RECEIPT_RELEASE_SHA="$DEPLOYED_SHA" \
  NF_RECEIPT_PROJECT="$PROJECT" \
  NF_RECEIPT_BRANCH="$BRANCH" \
  NF_RECEIPT_DEPLOYMENT_ID="$DEPLOYMENT_ID" \
  NF_RECEIPT_IMMUTABLE_URL="$IMMUTABLE_URL" \
  NF_RECEIPT_PAGES_ALIAS="$PAGES_ALIAS" \
  NF_RECEIPT_PROXY_OUTPUT="$PROXY_DEPLOY_OUT" \
  NF_RECEIPT_PROXY_STATUS="$PROXY_HTTP_STATUS" \
  NF_RECEIPT_PROXY_IDENTITY="$PROXY_IDENTITY" \
  NF_RECEIPT_PROXY_RELEASE="$PROXY_RELEASE" \
  NF_RECEIPT_PROXY_BODY_SHA256="$PROXY_BODY_SHA256" \
  NF_RECEIPT_PURGE_REQUESTED="${CF_PURGE_AFTER_DEPLOY:-0}" \
  NF_RECEIPT_PURGE_RESPONSE="$PURGE_RESPONSE" \
  NF_RECEIPT_MANIFEST_PATH="${ARTIFACT_MANIFEST#$ROOT/}" \
  NF_RECEIPT_MANIFEST_SHA256="$manifest_hash" \
  python3 - <<'PY'
import json
import os
from pathlib import Path


def value(name: str) -> str:
    return os.environ.get(name, "")


try:
    purge_result = json.loads(value("NF_RECEIPT_PURGE_RESPONSE"))
except json.JSONDecodeError:
    purge_result = {"raw": value("NF_RECEIPT_PURGE_RESPONSE")}

receipt = {
    "schema": "noetfield-www-deploy-receipt-v1",
    "success": True,
    "expected_sha": value("NF_RECEIPT_EXPECTED_SHA"),
    "release_sha": value("NF_RECEIPT_RELEASE_SHA"),
    "pages": {
        "project": value("NF_RECEIPT_PROJECT"),
        "branch": value("NF_RECEIPT_BRANCH"),
        "deployment_id": value("NF_RECEIPT_DEPLOYMENT_ID"),
        "immutable_url": value("NF_RECEIPT_IMMUTABLE_URL"),
        "production_alias": value("NF_RECEIPT_PAGES_ALIAS"),
    },
    "proxy": {
        "deployment_output": value("NF_RECEIPT_PROXY_OUTPUT"),
        "identity": {
            "url": "https://www.noetfield.com/api/health",
            "http_status": int(value("NF_RECEIPT_PROXY_STATUS") or "0"),
            "x_noetfield_proxy": value("NF_RECEIPT_PROXY_IDENTITY"),
            "x_noetfield_release": value("NF_RECEIPT_PROXY_RELEASE"),
            "body_sha256": value("NF_RECEIPT_PROXY_BODY_SHA256"),
        },
    },
    "cache": {
        "requested": value("NF_RECEIPT_PURGE_REQUESTED") == "1",
        "purged_urls": ["https://noetfield.com/*", "https://www.noetfield.com/*"],
        "result": purge_result,
    },
    "artifact_manifest": {
        "path": value("NF_RECEIPT_MANIFEST_PATH"),
        "sha256": value("NF_RECEIPT_MANIFEST_SHA256"),
    },
    "verification": {
        "success": True,
        "canonical_url": "https://www.noetfield.com",
        "post_deploy": "PASS",
    },
}
path = Path(value("NF_RECEIPT_PATH")).expanduser()
path.parent.mkdir(parents=True, exist_ok=True)
temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
temporary.replace(path)
print(f"[deploy-www-cloudflare] deployment receipt: {path}")
PY
}

EXPECTED_SHA="$(git rev-parse HEAD)"
if [[ ! "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  log "FAIL: git HEAD is not a full release SHA"
  exit 2
fi

CF_PROVIDER_TOKEN="$(provider_token)"
if [[ -z "$CF_PROVIDER_TOKEN" ]]; then
  log "FAIL: Cloudflare provider credential is unavailable"
  exit 2
fi

assert_clean_release_source "before build"
bash scripts/build-www-pages-dist.sh
python3 scripts/verify-public-output-allowlist.py
python3 scripts/build-public-www-artifact.py --mode verify
python3 scripts/verify_chat_greeting_coupling.py
assert_clean_release_source "after build"

ensure_project
sync_pages_secrets

COMMIT_MESSAGE="$(git log -1 --pretty=%s)"
log "deploy branch=${BRANCH} sha=${EXPECTED_SHA:0:12} wrangler=${WRANGLER_VERSION}"
DEPLOY_OUT="$("${WRANGLER[@]}" pages deploy www-pages-dist \
  --project-name "$PROJECT" \
  --branch "$BRANCH" \
  --commit-hash "$EXPECTED_SHA" \
  --commit-message "$COMMIT_MESSAGE" \
  --commit-dirty=false \
  --skip-caching 2>&1)"
printf '%s\n' "$DEPLOY_OUT"

if ! RELEASE_ROW="$(resolve_deployment "$EXPECTED_SHA")"; then
  log "FAIL: could not resolve an exact production deployment for ${EXPECTED_SHA}"
  python3 scripts/nf_post_deploy_verify.py --deploy-failed \
    "Cloudflare Pages exact deployment metadata missing" --surface www || true
  exit 2
fi
IFS=$'\t' read -r DEPLOYMENT_ID IMMUTABLE_URL DEPLOYED_SHA DEPLOYED_BRANCH DEPLOYED_ENVIRONMENT <<< "$RELEASE_ROW"
if [[ "$DEPLOYED_SHA" != "$EXPECTED_SHA" || "$DEPLOYED_BRANCH" != "$BRANCH" || "$DEPLOYED_ENVIRONMENT" != "production" ]]; then
  log "FAIL: resolved Pages deployment metadata does not match the requested release"
  exit 2
fi
log "Pages deployment id=${DEPLOYMENT_ID} url=${IMMUTABLE_URL}"

wait_for_service_health "$IMMUTABLE_URL" "$EXPECTED_SHA" || {
  log "FAIL: immutable Pages deployment health is unavailable"
  exit 3
}
verify_release_surface "$IMMUTABLE_URL" --expected-sha "$EXPECTED_SHA" \
  --surface www --skip-intake-e2e --provider-verified-release || {
  log "FAIL: immutable Pages deployment surface verification did not stabilize"
  exit 3
}

if [[ "$BRANCH" == "main" ]]; then
  wait_for_service_health "$PAGES_ALIAS" "$EXPECTED_SHA" || {
    log "FAIL: Pages production alias health is unavailable"
    exit 3
  }
  compare_release_content "$IMMUTABLE_URL" "$PAGES_ALIAS" "$EXPECTED_SHA" || {
    log "FAIL: Pages production alias does not serve the exact deployment content"
    exit 3
  }
  verify_release_surface "$PAGES_ALIAS" --expected-sha "$EXPECTED_SHA" \
    --surface www --skip-intake-e2e --provider-verified-release || {
    log "FAIL: Pages production alias surface verification did not stabilize"
    exit 3
  }

  if ! PROXY_DEPLOY_OUT="$(CF_WWW_ORIGIN="$IMMUTABLE_URL" \
    NF_WWW_RELEASE_SHA="$EXPECTED_SHA" \
      bash scripts/deploy-cf-www-proxy.sh 2>&1)"; then
    printf '%s\n' "$PROXY_DEPLOY_OUT" >&2
    log "FAIL: canonical Worker deployment or release-pin confirmation failed"
    exit 4
  fi
  printf '%s\n' "$PROXY_DEPLOY_OUT"

  confirm_proxy_pin "$EXPECTED_SHA" || {
    log "FAIL: canonical Worker does not expose the exact release pin"
    exit 4
  }
  compare_release_content "$IMMUTABLE_URL" "$CANONICAL" "$EXPECTED_SHA" || {
    log "FAIL: canonical Worker is pinned but does not serve exact release content"
    exit 4
  }

  if [[ "${CF_PURGE_AFTER_DEPLOY:-0}" == "1" ]]; then
    purge_public_host_cache
  fi

  confirm_proxy_pin "$EXPECTED_SHA" || {
    log "FAIL: canonical domain lost the exact release pin after cache action"
    exit 4
  }
  compare_release_content "$IMMUTABLE_URL" "$CANONICAL" "$EXPECTED_SHA" || {
    log "FAIL: canonical content differs after cache action"
    exit 4
  }
  VERIFY_ARGS=(--expected-sha "$EXPECTED_SHA" --surface www)
  if [[ "${NF_SKIP_INTAKE_E2E:-0}" == "1" ]]; then
    VERIFY_ARGS+=(--skip-intake-e2e)
  fi
  verify_release_surface "$CANONICAL" "${VERIFY_ARGS[@]}" || {
    log "FAIL: canonical surface verification did not stabilize"
    exit 4
  }
  write_deploy_receipt
fi

log "done — deployment_id=${DEPLOYMENT_ID} release=${EXPECTED_SHA} origin=${IMMUTABLE_URL}"
