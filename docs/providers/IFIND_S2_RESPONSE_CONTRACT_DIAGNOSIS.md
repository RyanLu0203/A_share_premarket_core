# iFinD S2 Response Contract Diagnosis

**Date:** 2026-08-13

**Mode:** offline-only; no provider call and no Keychain read
**Decision:** parser diagnostics hardened; S2 remains blocked and non-canonical

## Executive result

The first authorized S2 run stopped on
`002475.SZ:get_stock_info` with the generic failure
`IFIND_MCP_RESPONSE_SCHEMA_MISMATCH`. The retained local status proves only
that one of four permitted calls was attempted, no retry occurred, and no raw,
normalized, bundle, or canonical row was written. It does **not** retain enough
information to determine whether the rejected response failed at the JSON-RPC
layer, MCP result extraction, provider envelope, Markdown parsing, or S2 table
selection. Reconstructing a more specific cause from the old status would be
fabrication.

This checkpoint closes that diagnostic gap without another paid call. Future
failures carry only bounded, allowlisted response-shape metadata. No provider
cell, title, body excerpt, body hash, credential, header, request text, local
path, or raw exception message is persisted or returned to the Workspace.

## Dataset and grain

| Item | Contract |
| --- | --- |
| Acceptance cohort | exactly `002475.SZ` and `600487.SH` |
| S2 security grain | one `security_master` row per symbol |
| S2 market grain | 120 completed QFQ sessions per symbol |
| Reviewed units | shares=`股`; amount=`元`; turnover=`百分比/%` |
| Complete bundle | four artifacts and 242 normalized rows |
| Provider calls | two fixed tools × two fixed symbols; maximum four; zero retry |
| Historical failed scope | `002475.SZ:get_stock_info`, call 1/4 |
| Historical accepted S2 rows | 0 |

## Checks and findings

| Check | Result | Evidence quality |
| --- | --- | --- |
| Prior response body recoverable | No | raw persistence was correctly disabled |
| Prior failure layer recoverable | No | the old failure code covered multiple layers |
| Prior provider column set recoverable | No | no safe shape fingerprint existed at that time |
| S0 entitlement and input schemas | Accepted | 7/7 services; 35/35 entitled tools/schemas |
| S1 company identities | Accepted as metadata only | both symbols; zero canonical rows |
| S2 provider output schema | Not accepted | first call failed closed |
| S2 PIT/availability contract | Not evaluated | no normalized row reached the typed gate |
| S2 complete-bundle integrity | Implemented offline | fixture-backed reader; no live bundle exists |

## Implemented remediation

### Layered, metadata-only failure diagnosis

The MCP/S2 path now classifies failures into fixed stages such as
`jsonrpc_contract`, `mcp_result_extraction`, `provider_envelope`,
`provider_markdown`, `s2_table_selection`, `s2_semantic_validation`, and
`normalization`. Reasons are fixed enums, not provider or exception text.

The safe diagnostic may include only bounded counts, fixed required-column
presence, and SHA-256 fingerprints derived from response structure. The
fingerprint is value-independent: changing every provider cell while
preserving the same envelope, columns, and row count produces the same shape
fingerprint.

### Conservative parser compatibility

Offline fixtures now cover standard Markdown tables with or without outer
pipes, the previously observed exact code/company-name inversion, exact
single-scope six-digit symbol normalization, the reviewed
`首发上市日期 -> 上市日期` alias, and compact `YYYYMMDD` listing dates. These
compatibility rules do not relax identity, required-field, calendar, QFQ,
provider-availability, or PIT requirements.

The parser continues to reject conflicting MCP result variants, multiple or
ambiguous reviewed tables, unsafe formula cells, control characters, row-width
drift, missing fixed columns, cross-scope symbols, missing provider
availability, non-QFQ evidence, calendar drift, and any partial 242-row bundle.

### Accepted-bundle read boundary

The Workspace can consume a future S2 bundle only when the sanitized local
status is `PASS` and anchors both an immutable bundle id and an exact manifest
SHA-256. The reader uses one explicit external `ASHARE_PREMARKET_DATA_ROOT`;
it never discovers a latest bundle or falls back to another directory.

It revalidates private permissions, symlink/path confinement, the exact four-
file set, manifest and file hashes, recomputed request/schema/license lineage,
242-row count, primary-key uniqueness and order, normalized checksums, QFQ
semantics, the exact governed 120-session calendar, numeric domains, a single
provider availability timestamp per batch, and PIT timestamps. Security share
counts are accepted only when both units are explicitly `股`; market volume,
amount, and turnover are accepted only as `股`, `元`, and `百分比/%`. Any
failure rejects the whole bundle and exposes zero rows. Live accepted data is
never mixed row-by-row with Provider02B evidence, and immutable replay ignores
the external S2 overlay.

## Workspace behavior

- Provider Health may show only failure stage, fixed reason, bounded shape
  counts, a shortened shape fingerprint, fixed missing reviewed fields, and
  the explicit statement `raw_payload_persisted=false`.
- The old S2 status truthfully renders the diagnostic as not captured; it is
  not retroactively upgraded.
- Dual-stock pages distinguish S1 identity metadata, current S2 state, expected
  versus accepted rows, the fail-closed scope, and reference-portfolio
  membership.
- A future accepted S2 bundle may populate live security fields and the complete
  120-session QFQ chart only. Fundamentals, research, risk conclusions,
  recommendations, positions, orders, broker, trading, and production remain
  unchanged or locked.

## Remaining risk and next gate

The supplier's real `get_stock_info` and `get_stock_performance` output
contracts are still unaccepted. In particular, the project has not proven that
the purchased plan returns the reviewed provider availability, share fields
with explicit units, QFQ marker, market units, and complete 120-session shape
in one bounded response.

A future retry therefore requires new explicit owner authorization. The safest
sequence is one fixed `002475.SZ:get_stock_info` call after the merged diagnostic
checkpoint is deployed. If it still fails, the metadata-only shape evidence is
enough for another offline repair. No Hengtong or performance call should occur
after that first failure. Passing a parser check alone does not authorize S3,
S4, research, recommendation, position, or execution promotion.

## Validation matrix

The checkpoint is covered by offline tests for failure-layer classification,
value-independent fingerprints, status sanitization, standard Markdown,
known identity variants, required-column failures, normalization, bundle
manifest/hash/PIT/permission failures, live-only Workspace projection,
immutable replay preservation, GET-only API behavior, and frontend unavailable
states. No validation command accesses iFinD or macOS Keychain.
