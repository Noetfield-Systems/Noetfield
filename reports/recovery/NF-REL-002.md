# NF-REL-002 — Recoverable website baseline

## Authority and isolation

- Baseline: `e83aff92764c916362767f1dcb616bc3ece9535f` (`origin/main`).
- Recovery branch: `recovery/noetfield-www-baseline-2026-07-16`.
- Canonical dirty worktree was read only.
- The earlier detached reconciliation worktree and its generated reports were not imported.
- Canonical local source was captured before selection in the local-only ignored file
  `NF-REL-002-canonical-local.patch` (`sha256:a9d6ad5910e9f43e215ce1492390dd24ec180ae4d13a3d6c2238a6abd707e219`).
  It remains in the isolated recovery worktree and is intentionally not published in the PR.

## Canonical dirty-worktree inventory affecting this recovery

| File | Local change | Recovery selection |
|---|---|---|
| `_redirects` | Broad `/enterprise/` mount migration and Investors redirects | Excluded; conflicts with stable root routes and `/investors/` preservation |
| `about/index.html` | Richer institutional company explanation and current lane links | Selected |
| `assets/noetfield-gate-pages-v1.css` | Styles required by recovered corporate pages | Selected |
| `assets/partials/header.html` | Repoints the full public nav beneath `/enterprise/` | Excluded; part of unfinished mount migration |
| `assets/partials/footer.html` | Repoints the full public footer beneath `/enterprise/` | Excluded; part of unfinished mount migration |
| `assets/partials/offerings-strip.html` | Repoints offers beneath `/enterprise/` | Excluded; part of unfinished mount migration |
| `enterprise/index.html` | Newer Institutional Production OS variant | Captured but excluded; it removes the protected pilot CTA, institutional shell, and established proof structure |
| `functions/_middleware.js` | Generated broad `/enterprise/` redirects | Excluded; part of unfinished mount migration |
| `governance/www-pages-routes.json` | Redirects `/investors/` to `/investor-workflows/` | Excluded; conflicts with required `/investors/` artifact |
| `invest/index.html` | Links private-round flow to Investor Workflows | Selected |
| `investor-workflows/index.html` | Newer workspace-backed workflow paths | Selected |
| `motors/index.html` | Newer workspace-backed motor paths | Selected |
| `scripts/build-www-pages-dist.sh` | Mounts and rewrites the public tree beneath `/enterprise/` | Excluded |
| `scripts/generate-cf-redirects.py` | Generates broad `/enterprise/` redirects | Local version excluded; recovery branch has a separate Pages-compatibility fix |
| `scripts/generate-www-deny-middleware.py` | Generates broad `/enterprise/` redirects | Excluded |
| `scripts/verify-www-pages-dist.sh` | Accommodates mounted Copilot demo path | Local version excluded; recovery branch adds complete-artifact checks instead |
| `sitemap.xml` | Removes Investors URLs and updates unrelated timestamps | Excluded |
| `enterprise/agent-transformation/index.html` | New recovered Enterprise lane | Selected |
| `enterprise/application-factory/index.html` | New recovered Enterprise lane | Selected; AI Value link normalized to stable root route |
| `enterprise/copilot-governance/index.html` | New recovered Enterprise lane | Selected; existing product links normalized to stable root routes |
| `frontier-systems/index.html` | New page directly referenced by About and Enterprise | Selected |
| `frontier-systems/memo/index.html` | New page directly referenced by Frontier Systems | Selected |
| `governance/enterprise-route-prefixes-v1.json` | Prefix manifest for broad mount migration | Excluded |
| `scripts/generate-cf-www-proxy.py` | Generates a separate proxy implementation | Excluded; existing tracked proxy was repaired directly |
| `scripts/mount-enterprise-pages-in-dist-v1.py` | Copies the marketing tree beneath `/enterprise/` | Excluded |
| `scripts/prefix_enterprise_nav_hrefs_v1.py` | Rewrites shared nav links | Excluded |
| `scripts/prefix_enterprise_page_hrefs_v1.py` | Rewrites page links | Excluded |

## Git/history selections

- `index.html`: retained from the baseline. The three-direction Investor version at
  `73615e73ad51e65797320b728ef491bd9d3a1a2e` is preserved in history but was
  superseded by `8054406e72626ccee39327a4f2325f1db2f1a7be` and was not silently restored.
- `investors/index.html`: retained exactly from the baseline.
- `proof/`: retained exactly from the baseline, including client-zero labeling and evidence artifacts.
- `enterprise/index.html`: retained exactly from the baseline; the uncommitted replacement remains recoverable in the capture patch.
- `noetfield-favicon-512.png`: retained exactly from the baseline.
- Existing product pages and shared assets remain at their stable root routes.

## Recovered artifact matrix

| Route | SHA-256 | Title | H1 |
|---|---|---|---|
| `/` | `0d602e1d328cf7ff942fe87b1399968f1ec4d89a4f928351699758f164948cf0` | Noetfield Systems | Noetfield Systems |
| `/about/` | `dda92cd65ded6045a7ddd96a23d856c5a4ffe523c801e5c126f75515c90f4410` | About — Noetfield Systems Inc. | Noetfield Systems Inc. |
| `/investors/` | `0601ab0e65cfaa568e08cb555de4444ff2aedb44c8d3d12930d54b2fa4989659` | Investor — Noetfield Systems | Proof before pitch |
| `/proof/` | `93b493cfb0ee686857a754f2284eaa86361a310ad3de95deecb9de3b2df5b229` | Proof — Noetfield Systems | Evidence, not slides |
| `/enterprise/` | `7c46b7b2862c631b82dc69f78a4f3d6d606963be8c1582e002987424f29eddfa` | Noetfield — Copilot governance · Trust Brief · sandbox | Governed AI operations—from sandbox receipt to board-ready proof. |
| `/motors/` | `14e0d479b52101f800aacf6d2a90af4021ded84ae80b3b06eed10830ac0f20a5` | Motor & Custom Workflow — Noetfield Systems | Built around how you work |
| `/invest/` | `67eac43fe760aa090ba423e0887e2f7a7278a6944b2517efe762f25cca6260b5` | Invest — Noetfield Systems Inc. | Equity in Noetfield |
| `/noetfield-favicon-512.png` | `8e5821c32cf29cda3c88d5a425dc4d4fc2b2519c0be87ea4325dc3788ac726c3` | Binary | Binary |

Plain paths and `?nf_rel_002=1` variants returned `200` with identical hashes in
both the deterministic static server and local Cloudflare Pages emulation.

## Routing recovery

Local Pages emulation proved that Pages rejects absolute-host sources and `404`
statuses in `_redirects`. Host rules are now omitted from generated Pages rules;
denylist 404 behavior remains in generated `functions/_middleware.js`.

Proposed canonical topology, encoded but not deployed:

1. `noetfield.com/*` and `www.noetfield.com/*` enter `noetfield-www-proxy`.
2. Apex receives a `308` to `www`, preserving path and query.
3. `www` proxies the same path and query to `noetfield-www.pages.dev`.
4. Pages serves one complete `www-pages-dist` artifact plus the bundled Functions tree.

## `x-robots-tag: noindex`

The header is already present on the direct `noetfield-www.pages.dev` response,
before traffic passes through `noetfield-www-proxy`. No tracked `_headers` file,
Pages Function, Worker source, or generator in this repository sets it. Its source
is therefore provider-side Pages/project or zone response-header configuration,
not this repository.

Proposed separate change: inspect Cloudflare Pages project settings and zone
Rulesets with read-only provider access, identify the exact rule/version, retain
`noindex` for previews, and remove it only from the confirmed production custom
domain after explicit approval. This recovery PR does not change indexing.

## Verification

- Complete build: `520` files plus bundled Pages Functions.
- Protected routes and recovered linked pages: `200` locally.
- Query variants: identical status and hashes.
- Apex/www host-header variants: identical artifact bodies.
- Internal references from recovered pages: resolved or explicitly dynamic (`/api/`, `/workspace/`).
- Favicon: present, non-empty, and query-stable.
- `python3 scripts/check_repo_policy.py`: PASS.
- `git diff --check`: PASS.
- `make verify-static-www`: PASS in a clean checkout-equivalent. It now asserts the selected homepage, Investors, Proof, and Enterprise contracts precisely; superseded v42 homepage and Investor expectations remain in `tests/fixtures/www/historical-v42-protected-surface-expectations.json`.
- `node scripts/test-invest-access-control.mjs`: PASS. Unauthenticated, legacy-boolean, and forged-token requests redirect to sign-in; the session endpoint verifies the Supabase token before issuing an HttpOnly bearer cookie; the protected route reverifies that token on every read; authorized responses are `private, no-store`; and non-read methods return `405`.
- `node scripts/verify-www-deny-middleware.mjs`: PASS (`157/157`). Machine-readable results are in `reports/recovery/NF-REL-002-denylist-matrix.json`.
- Local Wrangler Pages runtime: PASS for all `157` security-matrix rows; required public routes and favicon returned `200` with query-stable hashes, while `/invest/?nf_rel_002=runtime` returned the expected sign-in `302`.

## PR #111 required-repair decisions

### Public conversion paths

- Motors: recovered copy remains, but all four public cards route to `/contact/` or a scoped `/contact/?topic=...` enquiry. No Motor card links directly to `/workspace/onboarding`, `/workspace/cognitive-dashboard`, or `/workspace/workspace`.
- Invest: `/invest/` remains behind `functions/invest/[[path]].js`; the static page is `noindex,nofollow`, hidden until authentication, and served only after the Pages Function successfully reverifies the Supabase bearer token held in its short-lived HttpOnly cookie. The former unsigned boolean cookie is rejected. The public `/investor-workflows/` link is labeled as product information rather than a discussion of the private round.
- About: recovered corporate-positioning copy is visibly labeled `Provisional corporate positioning` and pending NF-WEB-001 review. It was not expanded further.

### Denylist migration

The matrix exercises every former `404` route source, every current exact deny,
both root and nested probes for every deny prefix, query-string variants, and the
required `/governance/` and `/services/` cases. `/governance/` is an intentional
public product hub; its sensitive files and internal subtrees return `404`.
`/services/` has no directory index and returns `404`, while the two existing named
public service product routes remain in the artifact. Internal service prefixes are
middleware-denied. No protected repository source was downloadable in local Pages
runtime verification.

The canonical apex/WWW topology remains unchanged: apex permanently redirects to
WWW with path and query preserved, and WWW proxies one complete Pages artifact.

No cache purge, merge, deployment, or production mutation was performed.
