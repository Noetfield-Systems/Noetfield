#!/usr/bin/env bash
# Agent enforcement gate — memory, skills, rules, events, R-012/R-013 (fail-closed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-agent-enforcement ==="

# 1) Enforcement map
for f in \
  docs/ops/AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md \
  docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md \
  docs/ops/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

# 2) Memory version + R-012/R-013
mem=".cursor/agent-memory/MEMORY_LOCKED.yaml"
if [[ ! -f "$mem" ]]; then
  echo "FAIL missing $mem" >&2
  fail=1
else
  ver="$(grep -E '^version:' "$mem" | awk '{print $2}' || true)"
  if [[ -n "$ver" ]] && [[ "$ver" -ge 11 ]]; then
    echo "OK   memory version $ver (>= 11)"
  else
    echo "FAIL MEMORY_LOCKED.yaml version must be >= 11 (got: ${ver:-none})" >&2
    fail=1
  fi
  for rid in R-011 R-012 R-013; do
    if grep -q "$rid" "$mem" 2>/dev/null; then
      echo "OK   $rid locked"
    else
      echo "FAIL MEMORY_LOCKED.yaml missing $rid" >&2
      fail=1
    fi
  done
fi

# 3) Skills 001–010
for n in 001 002 003 004 005 006 007 008 009 010; do
  skill_path="$(ls .cursor/skills/SKILL-${n}-*.md 2>/dev/null | head -1 || true)"
  if [[ -n "$skill_path" ]] && [[ -f "$skill_path" ]]; then
    echo "OK   exists $skill_path"
  else
    echo "FAIL missing SKILL-${n}-*.md" >&2
    fail=1
  fi
done

# 4) Event registry + schema
for f in .cursor/events/REGISTRY.md .cursor/events/EVENT_SCHEMA.yaml; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

if grep -q '^schema_version:' .cursor/events/EVENT_SCHEMA.yaml 2>/dev/null; then
  echo "OK   event schema_version present"
else
  echo "FAIL EVENT_SCHEMA.yaml missing schema_version" >&2
  fail=1
fi

if grep -q 'R-012' .cursor/events/EVENT_SCHEMA.yaml 2>/dev/null; then
  echo "OK   event schema cites R-012"
else
  echo "FAIL EVENT_SCHEMA.yaml must cite R-012" >&2
  fail=1
fi

# 5) Cursor rules (11 .mdc files)
mdc_count="$(find .cursor/rules -maxdepth 1 -name '*.mdc' 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$mdc_count" -ge 11 ]]; then
  echo "OK   cursor rules ($mdc_count .mdc files)"
else
  echo "FAIL expected >= 11 .cursor/rules/*.mdc (got $mdc_count)" >&2
  fail=1
fi

# 6) Incidents registry
if [[ -f .cursor/incidents/REGISTRY.md ]]; then
  echo "OK   incidents REGISTRY.md"
else
  echo "FAIL missing .cursor/incidents/REGISTRY.md" >&2
  fail=1
fi

# 7) Enforcement map references eval→enforce chain
if grep -q 'verify-agent-enforcement' docs/ops/AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md 2>/dev/null \
   && grep -q 'SKILL-010' docs/ops/AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md 2>/dev/null; then
  echo "OK   enforcement map wired"
else
  echo "FAIL AGENTIC_ENFORCEMENT_MAP missing verify-agent-enforcement or SKILL-010" >&2
  fail=1
fi

# 8) Delegate scope checks (R-005)
chmod +x scripts/verify-agent-scope.sh
if ./scripts/verify-agent-scope.sh; then
  echo "OK   verify-agent-scope delegated"
else
  echo "FAIL verify-agent-scope failed inside enforcement gate" >&2
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-agent-enforcement passed."
  exit 0
fi
echo ""
echo "Fix enforcement stack before push. See docs/ops/AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md" >&2
exit 1
