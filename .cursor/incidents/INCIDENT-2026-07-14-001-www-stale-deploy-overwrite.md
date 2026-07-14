# INCIDENT-2026-07-14-001 — WWW stale deploy overwrote locked live (Investor leak)

| Field | Value |
|-------|--------|
| **Agent tag** | `nf-local-repo-agent` |
| **Agent display** | `[NF-LOCAL-REPO-AGENT]` |
| **Doc id** | incident-www-stale-deploy-overwrite-2026-07-14 |
| **Severity** | **P0** (founder-classified **critical** — week of locked live work ruined by stale ship) |
| **Status** | **open** |
| **Reporter** | founder |
| **Surfaces** | `www.noetfield.com/` · deploy path · agent www ship workflow |
| **Related** | INCIDENT-2026-07-06-001 (interactive downgrade) · R-012 |

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-07-14

---

## Summary

Cursor agents repeatedly **overwrite founder-locked live www** with **stale git HEAD** (last day / last week).

On 2026-07-14, while shipping Case Study #2 proof packaging, the agent:

1. Stashed newer dirty WIP (including homepage / enterprise gate progress)
2. Built and deployed **git HEAD** as a “clean scoped” www ship
3. Promoted that package to production

**Live result:** the public homepage again showed an **Investor** direction tile → `/investors/` (invest-in-Noetfield). Founder law: that surface on `/` is a **100% prohibited public leak**.

This is not a one-off mistake. It is a recurring agent pattern:

> Treat committed `main` as the product truth → stash local work → deploy HEAD → claim upgrade → **live is downgraded to last week**.

Founder impact: credits, time, and locked live pages are destroyed by the next agent “cleanup deploy.”

---

## What was locked / forbidden

| Law | Meaning |
|-----|---------|
| Direction gate on `/` | Enterprise · Motor (+ About · Proof) — **not** Investor |
| Invest-in-Noetfield | **Forbidden** on public homepage (`/investors/`, `/invest/`, “Investor” tile) |
| Live is a constraint | Production www may be **newer** than git HEAD; deploying HEAD can be a **regression** |
| Interactive anti-downgrade (R-012) | Do not shrink real sandbox/demo while shipping other work |

---

## Evidence (2026-07-14)

### 1. Agent deploy isolation pattern

```text
git stash push -u   # removes founder WIP from disk
bash scripts/deploy-www-cloudflare.sh   # ships whatever HEAD builds
# live overwritten with older committed HTML
```

Used during CS#2 www deploy to “isolate” proof files. Isolation of commit scope ≠ permission to ship stale full-site dist.

### 2. Live regression observed by founder

- Homepage again exposed **Investor** → `/investors/`
- Founder: invest-in-Noetfield on main page is **prohibited leak**
- Founder: agents “always downgrade every update” and restore “stale last week updates”

### 3. Corrective ship (same day)

- Commit `8054406e` — removed Investor/invest from homepage gate
- Commit `2710df84` — tests fail if Investor returns
- Production redeploy verified: live `/` shows **Enterprise** · **Motor** only (no Investor)

---

## Root cause

1. **Wrong SSOT for deploy:** Agents treat `git rev-parse HEAD` as “what should be live.” For www, **live + founder lock** can be newer than HEAD.
2. **Stash-then-deploy habit:** “Dirty tree is scary → stash → deploy clean HEAD” systematically ships **older** pages than the founder’s locked disk/live state.
3. **Full-site rebuild on every ship:** `build-www-pages-dist.sh` packages the whole site. A “small” proof commit still redeploys homepage/enterprise/etc.
4. **No live-vs-dist gate:** Deploy promoted without comparing the outbound package to **live** locked markers (anti-stale / anti-leak).
5. **CI green ≠ live fidelity:** Site-health on HEAD can pass while production is about to receive a regression relative to the prior live lock.

---

## Corrective actions

- [x] **T0 — Remove Investor/invest from live homepage** (`8054406e` + production deploy `2710df84`). Verified live: Enterprise · Motor only.
- [x] **E2E fail-closed** if homepage reintroduces `/investors/`, `/invest/`, or “Investor”.
- [x] **File this incident** + registry + MEMORY bump (R-014).
- [x] **Install mandatory pre-deploy anti-stale / protected-surface gate** — `scripts/nf_www_deploy_anti_stale_v1.py` + `config/noetfield-www-protected-surfaces.v1.json` (candidate PR; fail-closed). Live HTML is a constraint signal, not SSOT.
- [x] **Wire gate into** `scripts/deploy-www-cloudflare.sh` before `wrangler pages deploy` (requires `NF_AUTHORIZED_PROMOTE_SHA`).
- [x] **Commit universal change-preservation law** — `.cursor/rules/000-noetfield-universal-change-preservation-law-v1.mdc` (local alwaysApply alone is not repository control).
- [ ] **Founder promote** enforcement candidate (`CANDIDATE_PENDING_UNIVERSAL_POLICY_INTEGRATION`) + sign-off on protected-surface markers. Incident stays **open** until merge; no institutional closure from this checklist alone.

---

## Prevention (law)

### R-014 — Never deploy stale www over locked live

1. **Promotion chain:** founder-approved source SHA → verified build → exact-SHA promotion → verified public fingerprint → immutable receipt. Live HTML is **not** SSOT.
2. **Live is a deploy constraint.** Refuse candidates that regress locks already satisfied on production (`LIVE_AHEAD_OF_GIT`).
3. **Forbidden:** `git stash` (or clean checkout) of www WIP → deploy HEAD → overwrite live with older HTML.
4. **Forbidden on `/`:** Investor tile, `/investors/`, `/invest/`, “Invest in Noetfield”, or any invest-in-company CTA.
5. **Scoped commit ≠ scoped deploy.** Exact `NF_AUTHORIZED_PROMOTE_SHA` required; dirty/implicit HEAD promote refused.
6. **Fail closed.** HTTP 200 / CI green / marketing text alone are insufficient proof.

### Agent checklist (every www deploy)

```bash
# 1. Do NOT stash founder www WIP to get a "clean" tree
# 2. Build dist
bash scripts/build-www-pages-dist.sh
# 3. Exact authorized SHA must equal clean HEAD; gate must PASS
export NF_AUTHORIZED_PROMOTE_SHA="$(git rev-parse HEAD)"  # only after founder authorize that SHA
./scripts/deploy-www-cloudflare.sh   # invokes nf_www_deploy_anti_stale_v1.py --mode promote
# 4. Post-deploy verify + immutable receipt (not HTTP 200 alone)
```

---

## Apology

The agent prioritized “clean git isolation” and CI convenience over the founder’s locked live product. That shipped a prohibited Investor homepage entry and burned a week of locked work. That is a **critical production regression pattern**, not a minor process slip. **This incident stays open** until the anti-stale deploy gate is installed and wired.

---

## Authority

- Founder order 2026-07-14: invest-in-Noetfield on main page is prohibited; agents keep redeploying stale locks
- `docs/www/WWW_IMPLEMENTATION_STATUS_v1.md` — direction gate; no Investor on `/`
- R-012 — interactive anti-downgrade (related failure class)
- Deploy script: `scripts/deploy-www-cloudflare.sh` (`--commit-dirty=true` does not prevent HEAD-staleness after stash)
