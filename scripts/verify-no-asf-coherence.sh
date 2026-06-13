#!/usr/bin/env bash
# Meta-verify: merge truth, manifests, R-011, OPEN_PRS, canonical paths, registry fence.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-no-asf-coherence ==="

# R-011 + locked agentic law on disk
for f in \
  docs/ops/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md \
  .cursor/skills/SKILL-008-agentic-commercial-boundary.md; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

if grep -q 'R-011' .cursor/agent-memory/MEMORY_LOCKED.yaml 2>/dev/null; then
  echo "OK   R-011 in MEMORY_LOCKED.yaml"
else
  echo "FAIL MEMORY_LOCKED.yaml missing R-011" >&2
  fail=1
fi

# README canonical ship pointer
if grep -q 'os/SHIP_NOW.md' README.md 2>/dev/null && ! grep -q 'docs/SHIP_NOW.md' README.md 2>/dev/null; then
  echo "OK   README points to os/SHIP_NOW.md"
else
  echo "FAIL README must point to os/SHIP_NOW.md only (not docs/SHIP_NOW)" >&2
  fail=1
fi

if grep -q 'os/SHIP_NOW.md' docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md 2>/dev/null; then
  echo "OK   sprint backlog cites os/SHIP_NOW.md"
else
  echo "FAIL SPRINT_BACKLOG must cite os/SHIP_NOW.md" >&2
  fail=1
fi

# AGENT_READ_LINKS canonical ship
if grep -q 'Ship now (canonical)' docs/ops/AGENT_READ_LINKS_LOCKED_v1.md 2>/dev/null; then
  if grep -q 'docs/SHIP_NOW' docs/ops/AGENT_READ_LINKS_LOCKED_v1.md 2>/dev/null; then
    echo "FAIL AGENT_READ_LINKS lists docs/SHIP_NOW as co-primary" >&2
    fail=1
  else
    echo "OK   AGENT_READ_LINKS canonical ship link"
  fi
else
  echo "FAIL AGENT_READ_LINKS missing canonical ship label" >&2
  fail=1
fi

# SSOT_INDEX path — must resolve to docs/SSOT_INDEX.md (not docs/ops/)
if [[ -f docs/SSOT_INDEX.md ]]; then
  echo "OK   docs/SSOT_INDEX.md exists"
else
  echo "FAIL missing docs/SSOT_INDEX.md" >&2
  fail=1
fi
if [[ -f docs/ops/SSOT_INDEX.md ]]; then
  echo "FAIL docs/ops/SSOT_INDEX.md must not exist (use docs/SSOT_INDEX.md)" >&2
  fail=1
else
  echo "OK   no duplicate docs/ops/SSOT_INDEX.md"
fi
if grep -qE '\[SSOT_INDEX\.md\]\(\.\./SSOT_INDEX\.md\)' docs/ops/AGENT_READ_LINKS_LOCKED_v1.md 2>/dev/null; then
  echo "OK   AGENT_READ_LINKS SSOT_INDEX path correct"
else
  echo "FAIL AGENT_READ_LINKS must link ../SSOT_INDEX.md (not ./SSOT_INDEX.md)" >&2
  fail=1
fi

# Unified doc map + router
for f in docs/ops/DOCS_UNIFIED_MAP_LOCKED_v1.md docs/INDEX.md .cursor/skills/SKILL-009-docs-ssot-entry.md; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done
if grep -q 'QUICK_PICK precedence' docs/ops/DOCS_UNIFIED_MAP_LOCKED_v1.md 2>/dev/null \
   && grep -q 'GTM_NEXT open' docs/ops/plans/no-asf/QUICK_PICK.md 2>/dev/null; then
  echo "OK   QUICK_PICK precedence declared"
else
  echo "FAIL QUICK_PICK / unified map missing precedence rule" >&2
  fail=1
fi
if grep -q 'Registry synced' docs/ops/plans/INDEX.md 2>/dev/null && ! grep -qE '^| Done |' docs/ops/plans/INDEX.md 2>/dev/null; then
  echo "OK   plan registry INDEX metric clarified"
else
  if grep -q 'Registry synced' docs/ops/plans/INDEX.md 2>/dev/null; then
    echo "OK   plan registry INDEX metric clarified"
  else
    echo "FAIL plan INDEX still uses misleading Done: 1000" >&2
    fail=1
  fi
fi

# Prompt pack + agent context — GTM_NEXT precedence
if grep -qE 'GTM_NEXT.*first|GTM_NEXT wins' docs/ops/NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md 2>/dev/null \
   && grep -qE 'GTM_NEXT.*win|pick here first' docs/ops/plans/no-asf/QUICK_PICK.md 2>/dev/null \
   && grep -qE 'GTM_NEXT|Active ship queue' docs/ops/plans/README.md 2>/dev/null; then
  echo "OK   prompt pack GTM_NEXT precedence aligned"
else
  echo "FAIL prompt pack / plans README missing GTM_NEXT precedence" >&2
  fail=1
fi
if [[ -f docs/strategy/README.md ]] && [[ -f docs/DESIGN_SYSTEM.md ]] \
   && grep -q 'noetfield-institutional-v4' docs/DESIGN_SYSTEM.md 2>/dev/null; then
  echo "OK   strategy router + design system v4 indexed"
else
  echo "FAIL strategy README or DESIGN_SYSTEM v4 missing" >&2
  fail=1
fi

# GTM_NEXT and QUICK_PICK alignment
if [[ -f docs/ops/plans/no-asf/GTM_NEXT.md ]] && [[ -f docs/ops/plans/no-asf/QUICK_PICK.md ]]; then
  if grep -q 'GTM_NEXT' docs/ops/plans/no-asf/QUICK_PICK.md; then
    echo "OK   QUICK_PICK references GTM_NEXT"
  else
    echo "FAIL QUICK_PICK missing GTM_NEXT reference" >&2
    fail=1
  fi
  if grep -qE 'no open|Agentic only|ship-design-partner-outreach-026|^1\. \*\*ship-' docs/ops/plans/no-asf/QUICK_PICK.md; then
    echo "OK   QUICK_PICK GTM_NEXT inline"
  else
    echo "FAIL QUICK_PICK missing GTM_NEXT inline content" >&2
    fail=1
  fi
  if grep -q 'ship-procurement-openapi-verify-057' docs/ops/plans/no-asf/GTM_NEXT.md && grep -q 'ship-procurement-openapi-verify-057' docs/ops/plans/no-asf/QUICK_PICK.md; then
    echo "OK   QUICK_PICK mirrors GTM_NEXT iter 19"
  else
    echo "FAIL QUICK_PICK out of sync with GTM_NEXT iter 19 picks" >&2
    fail=1
  fi
  if grep -q 'Agentic only' docs/ops/plans/no-asf/GTM_NEXT.md && grep -q 'ship-design-partner-outreach-026' docs/ops/plans/no-asf/GTM_NEXT.md; then
    echo "OK   GTM_NEXT 026 in agentic section"
  else
    echo "FAIL GTM_NEXT missing agentic 026 section" >&2
    fail=1
  fi
else
  echo "FAIL missing GTM_NEXT or QUICK_PICK" >&2
  fail=1
fi

if grep -q 'GTM_NEXT' os/SHIP_NOW.md 2>/dev/null; then
  echo "OK   SHIP_NOW references GTM_NEXT"
else
  echo "FAIL SHIP_NOW missing GTM_NEXT reference" >&2
  fail=1
fi

if grep -q 'agentic only' docs/ops/plans/PROMPT_PACK_LOCKED/GTM_PRIORITY_100.md 2>/dev/null; then
  echo "OK   GTM_PRIORITY_100 agentic fence banner"
else
  echo "FAIL GTM_PRIORITY_100 missing agentic fence banner" >&2
  fail=1
fi

if rg -q 'implement: Design-partner outreach' docs/ops/plans/PROMPT_PACK_LOCKED/GTM_PRIORITY_100.md 2>/dev/null; then
  echo "FAIL GTM_PRIORITY outreach rows still use implement: Design-partner outreach" >&2
  fail=1
else
  echo "OK   GTM_PRIORITY outreach prompts are agentic-only"
fi

# Registry customer-outreach agentic_only
if command -v python3 >/dev/null 2>&1; then
  bad="$(python3 - <<'PY'
import json
from pathlib import Path
plans = json.loads(Path("docs/ops/plans/registry.json").read_text())["plans"]
bad = [p["id"] for p in plans if p.get("pattern") == "customer-outreach" and not p.get("agentic_only")]
print("\n".join(bad[:5]))
if len(bad) > 5:
    print(f"... and {len(bad)-5} more")
PY
)"
  if [[ -z "$bad" ]]; then
    echo "OK   registry customer-outreach rows have agentic_only"
  else
    echo "FAIL registry customer-outreach missing agentic_only:" >&2
    echo "$bad" >&2
    fail=1
  fi
fi

# plan.json done ship-* in manifest
manifest="docs/ops/plans/PROMPT_PACK_LOCKED/ENGINEERING_DONE_MANIFEST.md"
if [[ -f "$manifest" ]] && command -v python3 >/dev/null 2>&1; then
  missing="$(python3 - <<'PY'
import json, pathlib
data = json.loads(pathlib.Path("os/plan.json").read_text())
manifest = pathlib.Path("docs/ops/plans/PROMPT_PACK_LOCKED/ENGINEERING_DONE_MANIFEST.md").read_text()
missing = [t["id"] for t in data.get("next_tasks", []) if t.get("status") == "done" and t["id"].startswith("ship-") and t["id"] not in manifest]
print("\n".join(missing))
PY
)"
  if [[ -z "$missing" ]]; then
    echo "OK   plan.json ship-* done ids in ENGINEERING_DONE_MANIFEST"
  else
    echo "FAIL plan.json done ids missing from manifest:" >&2
    echo "$missing" >&2
    fail=1
  fi
fi

# SHIP_DONE_MAP completeness for done ship-* in plan.json
if command -v python3 >/dev/null 2>&1; then
  unmapped="$(python3 - <<'PY'
import json, re, pathlib
plan = json.loads(pathlib.Path("os/plan.json").read_text())
sync = pathlib.Path("scripts/sync-prompt-pack-status.py").read_text()
m = re.search(r"SHIP_DONE_MAP[^=]*=\s*\{([^}]+)\}", sync, re.S)
keys = set(re.findall(r'"([^"]+)":', m.group(1))) if m else set()
done_ids = [t["id"] for t in plan.get("next_tasks", []) if t.get("status") == "done" and t["id"].startswith("ship-")]
missing = [i for i in done_ids if i not in keys]
print("\n".join(missing))
PY
)"
  if [[ -z "$unmapped" ]]; then
    echo "OK   SHIP_DONE_MAP covers all done ship-* in plan.json"
  else
    echo "FAIL SHIP_DONE_MAP missing entries:" >&2
    echo "$unmapped" >&2
    fail=1
  fi
fi

# OPEN_PRS truth
if [[ -f docs/ops/plans/no-asf/OPEN_PRS.md ]]; then
  if grep -q 'closed 2026-06-10' docs/ops/plans/no-asf/OPEN_PRS.md && ! grep -q 'open until founder closes' docs/ops/plans/no-asf/OPEN_PRS.md; then
    echo "FAIL OPEN_PRS falsely claims stale PRs closed" >&2
    fail=1
  else
    echo "OK   OPEN_PRS stale PR wording"
  fi
  # ship-merged-window-config-056: MERGED_WINDOW from OPEN_PRS header
  merged_section="$(awk '/^## Recently merged/,/^## Stale PRs/' docs/ops/plans/no-asf/OPEN_PRS.md)"
  MERGED_WINDOW="$(grep -E '^\*\*MERGED_WINDOW:\*\*' docs/ops/plans/no-asf/OPEN_PRS.md 2>/dev/null | grep -oE '[0-9]+' | head -1 || true)"
  MERGED_WINDOW="${MERGED_WINDOW:-5}"
  if grep -qE '^\*\*MERGED_WINDOW:\*\*' docs/ops/plans/no-asf/OPEN_PRS.md 2>/dev/null; then
    echo "OK   OPEN_PRS MERGED_WINDOW documented (${MERGED_WINDOW})"
  else
    echo "FAIL OPEN_PRS missing MERGED_WINDOW header" >&2
    fail=1
  fi
  merged_pr_nums="$(echo "$merged_section" | grep -E '^\| #[0-9]+ \|' | head -n "$MERGED_WINDOW" | grep -oE '#[0-9]+' | tr -d '#' || true)"
  merged_count=0
  if [[ -n "$merged_pr_nums" ]]; then
    merged_count="$(echo "$merged_pr_nums" | wc -l | tr -d ' ')"
  fi
  if [[ "$merged_count" -lt "$MERGED_WINDOW" ]]; then
    echo "FAIL OPEN_PRS merged window: need ${MERGED_WINDOW} rows, got ${merged_count}" >&2
    fail=1
  else
    echo "OK   OPEN_PRS merged window (${MERGED_WINDOW} rows)"
    while IFS= read -r pr_num; do
      [[ -z "$pr_num" ]] && continue
      echo "OK   OPEN_PRS lists PR #${pr_num} merged (window)"
    done <<< "$merged_pr_nums"
  fi
  if echo "$merged_section" | grep -qE '^\| #40 \|'; then
    echo "OK   OPEN_PRS lists PR #40 merged"
  else
    echo "WARN OPEN_PRS missing merged PR #40"
  fi
  # ship-open-prs-autocheck-044: pending table must match gh open ship PRs
  if command -v gh >/dev/null 2>&1; then
    pending_section="$(awk '/^## Pending ship PR/,/^## Recently merged/' docs/ops/plans/no-asf/OPEN_PRS.md)"
    open_prs_doc="$(echo "$pending_section" | grep -E '^\| #[0-9]+ \|' | grep -oE '#[0-9]+' | tr -d '#' | sort -u | tr '\n' ' ' || true)"
    ship_prs_gh="$(gh pr list --state open --json number,headRefName --jq '.[] | select(.headRefName | test("^cursor/(no-asf|10-phase|post-audit|fourth-audit|fifth-audit|sixth-audit|seventh-audit|eighth-audit|ninth-audit|tenth-audit)")) | .number' 2>/dev/null | sort -u | tr '\n' ' ' || true)"
    open_prs_doc_trim="$(echo "$open_prs_doc" | xargs)"
    ship_prs_gh_trim="$(echo "$ship_prs_gh" | xargs)"
    if [[ -z "$open_prs_doc_trim" && -z "$ship_prs_gh_trim" ]]; then
      echo "OK   OPEN_PRS pending matches gh (no open ship PRs)"
    elif [[ "$open_prs_doc_trim" == "$ship_prs_gh_trim" ]]; then
      echo "OK   OPEN_PRS pending matches gh open ship PRs"
    else
      echo "FAIL OPEN_PRS pending (${open_prs_doc_trim:-none}) != gh ship PRs (${ship_prs_gh_trim:-none})" >&2
      fail=1
    fi
  fi
fi

# Buyer paths canonical
stale_paths="$(rg -l 'docs/reference/' copilot/ governance-console/ index.html trust-ledger/ docs/copilot/ 2>/dev/null || true)"
if [[ -z "$stale_paths" ]]; then
  echo "OK   buyer paths use docs/references/"
else
  echo "FAIL docs/reference/ in buyer-facing paths:" >&2
  echo "$stale_paths" >&2
  fail=1
fi

# docs/reference stub self-refs (warn)
stub_stale="$(rg -l 'docs/reference/' docs/reference/ 2>/dev/null | grep -v README || true)"
if [[ -n "$stub_stale" ]]; then
  echo "WARN docs/reference/ stubs with singular self-refs: $stub_stale"
else
  echo "OK   docs/reference/ stubs are redirect-only"
fi

# cursor-reply coherence (ship-cursor-reply-coherence-041 — FAIL not WARN)
reply="reports/cursor-reply-latest.txt"
main_sha="$(git rev-parse --short main 2>/dev/null || echo unknown)"
branch_name="$(git branch --show-current 2>/dev/null || echo unknown)"
if [[ -f "$reply" ]]; then
  if [[ "$branch_name" == "main" ]]; then
    reply_main="$(grep -E '^main: ' "$reply" 2>/dev/null | awk '{print $2}' || true)"
    if grep -qE "^main: ${main_sha}( |$)" "$reply" 2>/dev/null; then
      echo "OK   cursor-reply main: matches main ($main_sha)"
    elif [[ -n "$reply_main" ]] && git cat-file -e "${reply_main}^{commit}" 2>/dev/null \
         && git merge-base --is-ancestor "$reply_main" "$main_sha" 2>/dev/null \
         && [[ "$reply_main" != "$main_sha" ]]; then
      echo "OK   cursor-reply main: cites merge base ($reply_main) before closeout tip ($main_sha)"
    else
      echo "FAIL cursor-reply main: must match git rev-parse --short main ($main_sha)" >&2
      fail=1
    fi
  else
    reply_commit="$(git log -1 --format=%h -- "$reply" 2>/dev/null || echo unknown)"
    reply_only="$(git diff-tree --no-commit-id --name-only -r "$reply_commit" 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "$reply_only" == "1" ]] && git diff-tree --no-commit-id --name-only -r "$reply_commit" 2>/dev/null | grep -qx "$reply"; then
      expected_head="$(git rev-parse --short "${reply_commit}^" 2>/dev/null || echo unknown)"
    else
      expected_head="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
    fi
    if grep -qE "^head: ${expected_head}( |$)" "$reply" 2>/dev/null; then
      echo "OK   cursor-reply head: matches ship commit ($expected_head)"
    else
      echo "FAIL cursor-reply head: must match $expected_head (closeout cites ship SHA)" >&2
      fail=1
    fi
    if grep -qE "^main: ${main_sha}( |$)" "$reply" 2>/dev/null; then
      echo "OK   cursor-reply main: cites merge base ($main_sha)"
    else
      echo "FAIL cursor-reply main: must cite git rev-parse --short main ($main_sha)" >&2
      fail=1
    fi
  fi
else
  echo "FAIL missing reports/cursor-reply-latest.txt" >&2
  fail=1
fi

# PR warnings
if command -v gh >/dev/null 2>&1; then
  stale_prs="$(gh pr list --state open --json number,headRefName --jq '.[] | select(.headRefName | test("trustfield-scope|governance-console")) | .number' 2>/dev/null || true)"
  if [[ -n "$stale_prs" ]]; then
    echo "WARN stale out-of-scope PR(s) open: $stale_prs — founder should close"
  else
    echo "OK   no open trustfield-scope/governance-console PRs"
  fi
  ship_prs="$(gh pr list --state open --json number,headRefName --jq '.[] | select(.headRefName | test("^cursor/(no-asf|10-phase|post-audit|fourth-audit|fifth-audit|sixth-audit)")) | .number' 2>/dev/null || true)"
  if [[ -n "$ship_prs" ]]; then
    echo "WARN open ship PR(s): $ship_prs — merge before next iter closeout"
  else
    echo "OK   no open cursor ship PRs"
  fi
  if grep -q 'closed 2026-06-10' docs/ops/plans/no-asf/OPEN_PRS.md 2>/dev/null; then
    for pr in 2 7; do
      if gh pr view "$pr" --json state --jq .state 2>/dev/null | grep -q OPEN; then
        if grep -q "closed" docs/ops/plans/no-asf/OPEN_PRS.md 2>/dev/null && ! grep -q 'open until founder closes' docs/ops/plans/no-asf/OPEN_PRS.md; then
          echo "FAIL OPEN_PRS claims PR #$pr closed but GitHub shows open" >&2
          fail=1
        fi
      fi
    done
  fi
else
  echo "SKIP gh not available for PR checks"
fi

# Bank Pilot www — no false RPAA / BoC supervision claims (ship-fwd-075)
bank_pilot="${ROOT}/bank-pilot/index.html"
if [[ -f "$bank_pilot" ]]; then
  forbidden=(
    "RPAA registered"
    "Bank of Canada supervised"
    "registered with the Bank of Canada"
    "payment service provider registration"
  )
  bp_ok=1
  for phrase in "${forbidden[@]}"; do
    if grep -qiF "$phrase" "$bank_pilot" 2>/dev/null; then
      echo "FAIL bank-pilot contains forbidden claim: $phrase" >&2
      bp_ok=0
      fail=1
    fi
  done
  if [[ "$bp_ok" -eq 1 ]]; then
    echo "OK   bank-pilot no forbidden RPAA claims"
  fi
  if grep -qF "OSFI E-23" "$bank_pilot" && grep -qF "nf-policy-callout" "$bank_pilot"; then
    echo "OK   bank-pilot E-23 policy fence present"
  else
    echo "FAIL bank-pilot missing E-23 policy fence markers" >&2
    fail=1
  fi
else
  echo "FAIL missing bank-pilot/index.html" >&2
  fail=1
fi

# Federal lane — F only, no clearance or RPAA claims
federal_page="${ROOT}/federal/index.html"
if [[ -f "$federal_page" ]]; then
  if grep -qF "F lane lock" "$federal_page" && grep -qF "NIST AI RMF" "$federal_page"; then
    echo "OK   federal lane AIA/ADM/NIST markers"
  else
    echo "FAIL federal page missing F lane framework markers" >&2
    fail=1
  fi
  fed_forbidden=("security clearance granted" "RPAA registered" "Treasury Board approved")
  for phrase in "${fed_forbidden[@]}"; do
    if grep -qiF "$phrase" "$federal_page" 2>/dev/null; then
      echo "FAIL federal page forbidden claim: $phrase" >&2
      fail=1
    fi
  done
  echo "OK   federal lane claim fences"
else
  echo "FAIL missing federal/index.html" >&2
  fail=1
fi

# Unified 500 prompt pack — index + master + QUICK_PICK alignment
unified_json="docs/ops/plans/PROMPT_PACK_LOCKED/unified_500_index.json"
unified_master="docs/ops/plans/PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md"
unified_tiers="docs/ops/plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md"
unified_intel="docs/ops/plans/PROMPT_PACK_LOCKED/PICK_INTELLIGENCE_v1.md"
unified_gen="scripts/generate_unified_prompt_pack_500.py"
for f in "$unified_json" "$unified_master" "$unified_tiers" "$unified_intel" "$unified_gen"; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing unified 500 asset: $f" >&2
    fail=1
  fi
done
if command -v python3 >/dev/null 2>&1 && [[ -f "$unified_json" ]]; then
  unified_err="$(python3 - <<'PY'
import json, pathlib, sys
p = pathlib.Path("docs/ops/plans/PROMPT_PACK_LOCKED/unified_500_index.json")
data = json.loads(p.read_text())
errs = []
if data.get("count") != 500:
    errs.append(f"count={data.get('count')} expected 500")
if data.get("version") != "v4":
    errs.append(f"version={data.get('version')} expected v4")
next3 = data.get("next_3_recommended", [])
if len(next3) != 3:
    errs.append(f"next_3_recommended len={len(next3)} expected 3")
plans = data.get("plans", [])
if len(plans) != 500:
    errs.append(f"plans array len={len(plans)} expected 500")
top = data.get("top_25_ids", [])
if len(top) != 25:
    errs.append(f"top_25_ids len={len(top)} expected 25")
ids = [x["id"] for x in plans]
if len(set(ids)) != 500:
    errs.append("duplicate plan ids in unified index")
p0 = plans[0] if plans else {}
if "prompt_structured" not in p0 or "gtm_impact" not in p0:
    errs.append("plans missing v3 fields (prompt_structured, gtm_impact)")
if "prompt_redesigned" not in p0 or "goal_alignment" not in p0:
    errs.append("plans missing v4 fields (prompt_redesigned, goal_alignment)")
if "wisdom_score" not in p0 or "prompt_wise" not in p0:
    errs.append("plans missing v4 fields (wisdom_score, prompt_wise)")
if not data.get("sprint_themes"):
    errs.append("missing sprint_themes array")
fqs = [x.get("fq") for x in plans]
if len(set(fqs)) != 500 or min(fqs) != 1 or max(fqs) != 500:
    errs.append(f"fq coverage: unique={len(set(fqs))} min={min(fqs) if fqs else 0} max={max(fqs) if fqs else 0}")
print("\n".join(errs))
PY
)"
  if [[ -z "$unified_err" ]]; then
    echo "OK   unified_500_index.json structure (500 plans, top 25)"
  else
    echo "FAIL unified_500_index.json:" >&2
    echo "$unified_err" >&2
    fail=1
  fi
fi
for f in docs/ops/plans/PROMPT_PACK_LOCKED/PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md \
         docs/ops/plans/PROMPT_PACK_LOCKED/ALL_500_TIER_INDEX_v1.md \
         docs/ops/plans/PROMPT_PACK_LOCKED/WISDOM_PICK_RULES_v1.md; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing v4 asset: $f" >&2
    fail=1
  fi
done
if [[ -f docs/ops/plans/no-asf/QUICK_PICK.md ]]; then
  if grep -q 'UNIFIED_500_MASTER_v1' docs/ops/plans/no-asf/QUICK_PICK.md \
     && grep -q 'PICK_INTELLIGENCE_v1' docs/ops/plans/no-asf/QUICK_PICK.md \
     && grep -q 'SUCCESS_MODEL_TIERS_v1' docs/ops/plans/no-asf/QUICK_PICK.md \
     && grep -q 'WISDOM_PICK_RULES_v1' docs/ops/plans/no-asf/QUICK_PICK.md \
     && grep -q 'generate_unified_prompt_pack_500' docs/ops/plans/no-asf/QUICK_PICK.md; then
    echo "OK   QUICK_PICK unified 500 references"
  else
    echo "FAIL QUICK_PICK missing unified 500 references" >&2
    fail=1
  fi
fi
if [[ -f "$unified_master" ]] && [[ -f "$unified_json" ]] && command -v python3 >/dev/null 2>&1; then
  if grep -q 'Next 3 recommended' "$unified_master" && grep -q 'Suggested iter bundles' "$unified_master"; then
    echo "OK   UNIFIED_500_MASTER v2 sections (next 3 + bundles)"
  else
    echo "FAIL UNIFIED_500_MASTER missing v2 sections" >&2
    fail=1
  fi
  master_top="$(grep -cE '^[0-9]+\. \*\*ship-fwd-' "$unified_master" 2>/dev/null || true)"
  master_top="${master_top:-0}"
  if [[ "$master_top" -ge 25 ]]; then
    echo "OK   UNIFIED_500_MASTER top 25 section"
  else
    echo "FAIL UNIFIED_500_MASTER missing top 25 picks (found $master_top)" >&2
    fail=1
  fi
fi

# Client-safe copy — no competitor/vendor names on www or prompt pack
FORBIDDEN_VENDOR_RE='Vanta|Inforcer|Veridra|Credo|Drata|OneTrust|Holistic|Fiddler|Gateplex|Cloudiway|AvePoint|Lighthouse|ADJUDON|Audital|Trinitite|Modulos|benchmark-ui|BENCHMARK_SYNTHESIS|INSTITUTIONAL_BENCHMARK|COPILOT_COMPLEMENT_BENCHMARK|Typical GRC|Microsoft Purview|Microsoft 365|\\bM365\\b'
vendor_fail=0
vendor_paths=(
  index.html
  copilot/index.html
  trust-center/index.html
  trust-ledger/index.html
  partners/index.html
  partners/msp/index.html
  federal/index.html
  enterprise/index.html
  copilot/procurement/index.html
  docs/ops/plans/PROMPT_PACK_LOCKED/unified_500_index.json
  docs/ops/plans/PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md
  docs/copilot/PROCUREMENT_ONE_PAGER.md
  docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md
  docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md
  docs/diligence/POSITIONING_CLIENT_SYNTHESIS_v1.md
)
for vf in "${vendor_paths[@]}"; do
  if [[ -f "$vf" ]] && grep -qiE "$FORBIDDEN_VENDOR_RE" "$vf" 2>/dev/null; then
    echo "FAIL forbidden vendor/compare string in $vf" >&2
    grep -niE "$FORBIDDEN_VENDOR_RE" "$vf" 2>/dev/null | head -3 >&2 || true
    vendor_fail=1
  fi
done
if [[ "$vendor_fail" -eq 0 ]]; then
  echo "OK   client-safe copy guard (no vendor names on www/prompt pack)"
else
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-no-asf-coherence passed."
  exit 0
fi
exit 1
