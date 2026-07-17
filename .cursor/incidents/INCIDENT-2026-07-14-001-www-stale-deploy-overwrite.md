# INCIDENT-2026-07-14-001 — WWW stale deploy overwrote locked live (Investor leak)

| Field | Value |
|-------|--------|
| **Agent tag** | `nf-local-repo-agent` |
| **Agent display** | `[NF-LOCAL-REPO-AGENT]` |
| **Doc id** | incident-www-stale-deploy-overwrite-2026-07-14 |
| **Severity** | **P0** (founder-classified **critical** — week of locked live work ruined by stale ship) |
| **Status** | **closed** — 2026-07-17 |
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
- [x] **Install mandatory pre-deploy anti-stale gate** — v2 compares `www-pages-dist` to live `www.noetfield.com` for protected surfaces and fails closed if the package regresses or leaks prohibited content.
- [x] **Wire gate into** `scripts/deploy-www-cloudflare.sh` before `wrangler pages deploy`.
- [x] **Cursor rule:** NEVER stash www WIP then deploy HEAD to “isolate” a scoped change.
- [x] **Founder sign-off** on the v2 protected-surface contract and incident closure, given explicitly on 2026-07-17.

---

## Prevention (law)

### R-014 — Never deploy stale www over locked live

1. **Live is a deploy constraint.** Before production www promote, the outbound dist must be checked against live locked pages.
2. **Forbidden:** `git stash` (or clean checkout) of www WIP → deploy HEAD → overwrite live with older HTML.
3. **Forbidden on `/`:** Investor tile, `/investors/`, `/invest/`, “Invest in Noetfield”, or any invest-in-company CTA.
4. **Scoped commit ≠ scoped deploy.** If dist includes pages you did not intend to change, you must either exclude them or prove they are not a regression vs live.
5. **Fail closed** on anti-stale / anti-leak check. Do not promote on “CI passed” alone.

### Agent checklist (every www deploy)

```bash
# 1. Do NOT stash founder www WIP to get a "clean" tree
# 2. Build dist
bash scripts/build-www-pages-dist.sh
# 3. Anti-stale / anti-leak vs live (mandatory once script lands)
python3 scripts/nf_www_deploy_anti_stale_v2.py --dist www-pages-dist --live https://www.noetfield.com
# 4. Only then: deploy-www-cloudflare.sh + post-deploy verify
```

---

## Apology

The agent prioritized “clean git isolation” and CI convenience over the founder’s locked live product. That shipped a prohibited Investor homepage entry and burned a week of locked work. That is a **critical production regression pattern**, not a minor process slip. The incident was closed only after the v2 fail-closed guard was independently reviewed, merged, deployed from exact `main`, and verified live.

---

## Closure evidence — 2026-07-17

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-07-17

Founder explicitly authorized review, merge, exact-SHA deployment, and closure of this P0 incident. Closure is supported by the following immutable evidence:

| Evidence | Exact value |
|----------|-------------|
| Guard implementation PR | `#119` — `Fix P0 WWW stale-deployment guard` |
| Reviewed candidate SHA | `ce85b64b93a5e1971bb6d24acd85b812a7a652f2` |
| Normal merge / deployed `main` SHA | `e0165192cd625366bb95a8f682db14e1facff58f` |
| Production workflow | `Noetfield WWW Production` run `29562673649` — **PASS** |
| Cloudflare Pages deployment | `05debd27-97ba-40dd-8fca-26a0f47986eb` |
| Immutable origin | `https://05debd27.noetfield-www.pages.dev` |
| Production receipt SHA-256 | `d7f9e599d1be5380e1f17078083cc8d4aec34ad3e3c416f5e285a9d66ee8ce83` |
| Workflow evidence artifact | `8399916713` — ZIP SHA-256 `e1845a9d5b436fd6f23a43d4839d4622752e0cbcfceb26d2c993eec635c29edb` |

The production workflow checked out the exact merge SHA, passed the exact-release verification before deployment, deployed that SHA, uploaded five evidence files, and posted the receipt back to PR `#119`. Post-deploy verification passed at `https://www.noetfield.com`; both the canonical health endpoint and immutable Pages origin returned `git_sha=e0165192cd625366bb95a8f682db14e1facff58f`, and the canonical response carried `x-noetfield-release` with the same full SHA.

The v2 guard protects `/`, `/about/`, `/enterprise/`, `/motors/`, and `/proof/`; enforces the homepage investor-leak denylist; preserves interactive-surface markers; binds deployment authorization to an exact candidate SHA; and emits a deterministic anti-stale receipt. It intentionally supersedes the v1 route assumption: `/investors/` is now the public Ecosystem evidence page and `/investor-workflows/` is a governed product route, while invest-in-Noetfield CTAs remain prohibited on `/`.

**Closure verdict:** the mandatory anti-stale gate is installed and wired before promotion, the agent rule is present, exact-SHA production evidence is archived, and the protected live release matches the authorized merge. P0 `INCIDENT-2026-07-14-001` is therefore **closed**.

---

## Authority

- Founder order 2026-07-14: invest-in-Noetfield on main page is prohibited; agents keep redeploying stale locks
- `docs/www/WWW_IMPLEMENTATION_STATUS_v1.md` — direction gate; no Investor on `/`
- R-012 — interactive anti-downgrade (related failure class)
- Deploy script: `scripts/deploy-www-cloudflare.sh` (`--commit-dirty=true` does not prevent HEAD-staleness after stash)
