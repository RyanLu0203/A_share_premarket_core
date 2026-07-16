# Issue #36 architecture baseline reconciliation

## Scope

Issue #36 changes the operational stock-history source contract and advances
the truthful latest immutable snapshot from 2026-07-15 to 2026-07-16. It does
not change the OpenAPI schema, route topology, historical replay contract, or
locked capabilities.

## Inputs and causality

The changed architecture inputs are limited to:

- the daily refresh manifest and validation for the new complete Tencent
  current-T-1 batch;
- the OPM latest pointer and immutable 2026-07-16 snapshot;
- read-only response projections that intentionally expose current refresh,
  risk, provenance, or snapshot state.

The canonical historical market-data artifact remains byte-identical at
`4c5fa34d55ebbc327deee12f05ff120c0fe90db89c15dc0b995fee5aa96f4c4b`.
OpenAPI remains byte-identical at
`9d9d4814721de2c864907c0f57c39217346b61069fdca8892ab792fa5373e017`.
Seventeen API response hashes remain unchanged. The five intentionally changed
GET projections are `/api/command-center`, `/api/experiment`,
`/api/portfolio/risk`, `/api/provenance`, and `/api/snapshots`.

The three updated critical-artifact hashes are:

- daily refresh manifest:
  `bbbe7481d1510869c68bad200338e227a5304e8fb77fe3bb96e65e17642f98cc`;
- daily refresh validation:
  `0973abb9a1535bddb49474b020ff502ec34537d997b38cb072ff3a8d7cb03335`;
- OPM latest pointer:
  `a12cf310e6df259c3332260aee1f08701029ffedef0d58f8946094a2a9d56c26`.

## Preserved contract

Architecture parity still requires 22 GET routes and zero write routes. The
workspace remains read-only, `ready_factor_count` remains zero, and all
recommendation, trading, broker, production-model, factor-mining, and DQN/RL
locks remain unchanged. The reconciliation records truthful live operational
evidence; it is not a deployment-completion claim.
