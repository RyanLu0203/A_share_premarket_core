# PR #33 Blocked Runtime Baseline Reconciliation

## Decision

PR #33 preserves `BLOCKED` as the current operational truth. Code and canonical
contract validation may pass while operational deployment remains blocked. No
current snapshot exists, and deterministic replay is not live evidence.

The original architecture baseline commit remains
`e17a114aec8ea2f2f29259e5508e123f0f5486cc`. This reconciliation changes only
the baseline fields whose committed inputs intentionally changed in PR #33.

## Exact Changed Inputs

| Baseline field | Old SHA-256 | Reconciled SHA-256 | Exact input |
|---|---|---|---|
| `daily_refresh_manifest_sha256` | `0262dff84118eeba1f1d4ba37e8890eb28146ef55e2558814b071c169bad2dad` | `21fcf987e52110cd709fc274ee43efd28e72b4cfe6eeaccc0a6324f84012f064` | blocked live refresh manifest |
| `daily_refresh_validation_sha256` | `2542af6e57b0acac3e6bd7c282c00c1adf0dff9202aec18b17225af600ea4f54` | `ab1fe37accc9798522d8803a631919a561b7f31ac36c53af27ce041e4e8b0f84` | fail-closed validation rows |
| `/api/experiment` | `734717fb7970b1a9650468e1788b7c5590cb57d6aafdc9fc8e19fa23b68b039e` | `7a4b14f4c9c2d83fa6699941c16d689726f6e910e471f45cc52e06467b385e8a` | daily refresh experiment contract |
| `/api/provenance` | `092c8701e17819e28dc46ecf5565e1b1aeb37f88cac7f54e7db175de1a7367c8` | `50a4cfe81007546f0cbce770e4aee2671ed0d05a87f0e84e10b021a90716d27e` | latest refresh pointer plus verified manifest integrity |

`collect_doctor_report` reads `refresh_status` directly from
`outputs/research/daily_incremental_evidence_refresh/latest_refresh.json`.
Its expected value is deliberately changed from `SUCCEEDED` to `BLOCKED`.

## Causality Proof

- All 22 projected GET responses were recalculated. Only `/api/experiment`
  and `/api/provenance` differed from the prior hashes.
- Replacing only `daily_refresh_contract` in the current experiment response
  with the `origin/project-current` contract reproduces the former experiment
  hash exactly.
- Replacing only `daily_refresh` in the current provenance response with the
  `origin/project-current` refresh pointer and its `VERIFIED` integrity field
  reproduces the former provenance hash exactly.
- The experiment difference is only `snapshot_lineage`, changing from the
  historical `2026-07-01` snapshot path to `no_valid_snapshot`.
- The provenance differences are only refresh evidence fields: execution and
  evidence mode, dates, blocked reasons, manifest lineage/checksum, status,
  validation, and empty current-snapshot fields.
- No API route implementation, experiment repository implementation,
  provenance repository implementation, OpenAPI contract, immutable snapshot,
  or canonical market-data artifact changed as a contributor to these hashes.

## Validation And Operational Separation

Architecture parity is successful only when all five critical artifact hashes,
OpenAPI, all 22 projected GET response hashes, and locked boundaries match the
reconciled contract. Separately, operational readiness remains `BLOCKED` until
a complete current T-1 batch creates a checksum-verified current snapshot.

The deterministic replay integration test backs up and restores all seven
mutable operational refresh outputs. This preserves replay validation while
preventing a test run or the canonical profile from rewriting committed live
state as `SUCCEEDED`.

Recommendation, trading, broker, production, factor-mining, and DQN/RL remain
locked.
