# Issue #34 requirement completion audit

## Decision

Issue #34 is complete as a governed infrastructure repair and current
research-only live refresh.  It is eligible for review in a feature-branch PR
into `project-current`; it is not a deployment, launchd, service-start, trading,
or downstream-unlock claim.

## Authoritative source and branch

- Base: `origin/project-current` at
  `c7a271fefe12936266de73fedfad233869e4d79e` (merged PR #33).
- Branch: `codex/governed-akshare-tencent-secondary-upstream`.
- AKShare remains the application provider.
- East Money `stock_zh_a_hist` remains primary.
- Tencent `stock_zh_a_hist_tx` is the only governed secondary.

## State-machine acceptance

- Primary batch: 41/41 bounded requests completed first; 0 accepted, 41
  `BROWSER_NET_EMPTY_RESPONSE`, no local/proxy/TLS/integrity failure.
- Failure evaluation: performed only after primary termination; activation
  reason `APPROVED_PRIMARY_ENDPOINT_FAILURE`.
- Secondary batch: complete reacquisition, 41/41 accepted exact 2026-07-14
  rows, schema/PIT/provenance/coverage/source-consistency all PASS.
- Selected source: Tencent only; East Money partial candidates discarded;
  `no_per_symbol_mixing=true`.
- Selected normalized batch SHA-256:
  `a95459ff4be28e5acf48c7fb056490f470034d6949599119da8fa8277b95f5b5`.

## qfq and field semantics

- Production adjustment is qfq only.
- Ordinary qfq overlap passes for SSE, SZSE, and ChiNext.
- SSE `603836.SH` and required-universe SZSE `000333.SZ` corporate actions
  pass authoritative-terms triangulation, approved-calendar alignment,
  unadjusted structural checks, qfq formula checks, and continuity checks.
- Missing primary corporate rows are classified
  `PRIMARY_CORPORATE_ACTION_EVIDENCE_UNAVAILABLE`.
- hfq remains runtime-disabled and non-production. Its bounded 600036.SH
  discrepancy remains recorded as a non-blocking research finding.
- AKShare's Tencent sixth field is volume in `手`, scale 1. Monetary `amount`
  is canonical null with `TENCENT_AMOUNT_UNAVAILABLE`; null is tested distinct
  from observed zero, and any consumer declaring amount required fails closed.

## Live acceptance and idempotency

- Calendar provider/function: AKShare / `tool_trade_date_hist_sina`.
- Calendar SHA-256:
  `db13387fd42cb1ef98bbde07a12d2f8c64c438eeea940926d4ec49b2a5263d14`.
- 2026-06-19 is closed.
- Target / T-1: `2026-07-15` / `2026-07-14`.
- Execution mode / evidence mode: `daily_operational` /
  `live_bounded_fetch`; deterministic replay was not used.
- Snapshot ID: `opm:2026-07-15:8bb1154998565855`.
- Snapshot SHA-256:
  `8bb115499856585595e1f6e625bbea3e8d6de7c89a067992c2af9fe62685e3d2`.
- Canonical evidence SHA-256:
  `88f2571000e740042bbd5acc8085267fbfd9fa1f8e8828eedf4a2356437d1052`.
- Refresh manifest SHA-256:
  `bc9f8424495477b289e78b35ab74137b461bf3cc91a395853a8179ba6b04b84f`.
- Git-bounded reconstruction evidence: the committed predecessor canonical
  base (`4c5fa34d55ebbc327deee12f05ff120c0fe90db89c15dc0b995fee5aa96f4c4b`)
  plus a 41-row T-1 delta
  (`ca903f09c2183082558c4938812667a8d4435377f246b61553e290c72ca9a49a`)
  reconstructs the full canonical evidence checksum exactly. The versioned
  commitment is stored beside the immutable refresh manifest.
- Second full run used the same frozen execution time and runtime calendar; it
  did not use `already_refreshed`.
- Idempotency:
  `PASS_IDENTICAL_NORMALIZED_BATCH_AND_IMMUTABLE_SNAPSHOT`; selected source,
  batch checksum, canonical checksum, snapshot checksum, and manifest checksum
  are identical.

An interrupted pre-fix attempt exposed that OPM independently sampled a second
wall-clock timestamp. Atomic guards preserved the first snapshot. The refresh
now passes its already-resolved clock into OPM, and a regression test covers
the boundary. All pre-fix and failed-attempt artifacts are preserved only in
ignored `outputs/local/runtime/` diagnostics and are excluded from the PR. The
12.4 MB duplicate full canonical materialization also remains ignored; the
bounded delta and cryptographic reconstruction commitment make a fresh clone
independently verifiable without committing the duplicate market dataset.

## Validation

- Python 3.12 compileall: PASS.
- Full Python: `448 passed`, one non-blocking Starlette/httpx deprecation
  warning.
- Canonical program profile: `117/117 PASS`.
- Stock-chart architecture run/audit: PASS.
- Workflow status/cleanliness, safety, adapter, provider-failure taxonomy,
  feature-label leakage, engineering PIT, PIT snapshot, and macOS prerequisite
  checks: PASS.
- OpenAPI: unchanged; 22 GET routes and zero write routes.
- Architecture baseline reconciliation: exactly five read-only API projections
  changed due the truthful second snapshot/current refresh evidence; 17 stayed
  exact. See
  `docs/architecture/refactor01/ISSUE34_LIVE_RUNTIME_BASELINE_RECONCILIATION.md`.

## Boundaries

Recommendation, target-price, position execution, trading, broker,
production-model, factor-mining, and DQN/RL remain locked. No launchd agent was
installed or changed, and no backend/frontend service was started by Issue #34.
