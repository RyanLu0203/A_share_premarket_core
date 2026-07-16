# Issue #34 live-runtime architecture baseline reconciliation

## Decision

The architecture baseline is deliberately reconciled to the validated
Issue #34 live result.  Code and canonical interface validation remain a
separate concern from runtime readiness: the interface surface is still 22 GET
routes and zero write routes, while the operational state moved truthfully from
`BLOCKED` to `SUCCEEDED` only after a complete qfq Tencent batch and two-run
idempotency validation.

This is not a tolerance relaxation.  OpenAPI, the committed canonical market
dataset, the historical 2026-07-01 replay snapshot, all locks, and 17 of 22
projected API response hashes remain byte-for-byte unchanged.

## Critical artifact changes

| Artifact | PR #33 baseline SHA-256 | Issue #34 SHA-256 | Intentional input |
|---|---|---|---|
| daily refresh manifest | `21fcf987e52110cd709fc274ee43efd28e72b4cfe6eeaccc0a6324f84012f064` | `bc9f8424495477b289e78b35ab74137b461bf3cc91a395853a8179ba6b04b84f` | blocked 7/15 attempt replaced by complete, checksummed qfq live acquisition evidence |
| daily refresh validation | `ab1fe37accc9798522d8803a631919a561b7f31ac36c53af27ce041e4e8b0f84` | `1e63f895b8e0ce17e61ba49dfdca883a5451b1afc9662de7bb6e4ab080bc27bb` | freshness, coverage, schema, PIT, provider, and checksum gates now PASS |
| OPM latest pointer | `6013ab98b47f07a80a4fd94f4fb81e1f43a457461a848452d87427ed971889d7` | `29658051c00835129089c239e3e579c32e27c219c67d59a594f8d3e46deb6c73` | latest verified snapshot moved from 2026-07-01 to 2026-07-15 |

The canonical market artifact hash remains
`4c5fa34d55ebbc327deee12f05ff120c0fe90db89c15dc0b995fee5aa96f4c4b`.
The historical 2026-07-01 OPM snapshot manifest remains
`7e3e680451068ff859460e0c3e55e62b4d95a994773bf0e00e68e90f691e679e`.
The live 2026-07-15 snapshot manifest is
`8bb115499856585595e1f6e625bbea3e8d6de7c89a067992c2af9fe62685e3d2`.

## API response changes

Exactly five projected GET responses changed:

| Route | PR #33 SHA-256 | Issue #34 SHA-256 | Exact payload delta |
|---|---|---|---|
| `/api/command-center` | `7b45a36da17160e287738c83227d75f97237367778574789be40f55fbc9c626f` | `47da87b1cfb650875c58e85010346056e3596c0004e3307746e210b1f0039fa7` | risk history length 1 -> 2 |
| `/api/portfolio/risk` | `d8e2895f8142b4a11aaf2368ac09c04d068cf01ce04dc0fb6ccac79ded898957` | `068298f6d518b7bd51c7e0c706a1fc18f05e2177925c294b12d9074fa1c50e34` | history length 1 -> 2 |
| `/api/experiment` | `7a4b14f4c9c2d83fa6699941c16d689726f6e910e471f45cc52e06467b385e8a` | `544635861b01d6c04fd7b0873aaae80163bf2155cbb1e0c02cf3153abdc34f48` | snapshot lineage now points to the verified 7/15 snapshot; freeze dates/mode reflect daily operational evidence |
| `/api/snapshots` | `056ae144f81b5dd3d9a972a0afe624dd6e713b5d329ef15c530695b64fe08a1c` | `121409b6539c3ca4d7496404cf9960c2de0dfb668417c88fb605c86678fdf395` | latest 7/01 -> 7/15; snapshot count 1 -> 2 |
| `/api/provenance` | `50a4cfe81007546f0cbce770e4aee2671ed0d05a87f0e84e10b021a90716d27e` | `601e817c00e292d6d27c01e7fba7bc0a038e64fd61af5e3750c91e47831adc64` | blocked reasons cleared; SUCCEEDED, snapshot/checksum, Tencent selection, and idempotency evidence added |

These deltas were reproduced by comparing a detached
`origin/project-current` worktree at
`c7a271fefe12936266de73fedfad233869e4d79e` with the current feature branch.
No route implementation changed as part of this reconciliation.

## Locked boundaries

Recommendation, target-price, position execution, trading, broker,
production-model, factor-mining, and DQN/RL capabilities remain locked.  The
new snapshot is research-only and not for execution.
