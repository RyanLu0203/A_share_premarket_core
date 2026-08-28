# GOAL-LIQUIDITY-SCHEMA-SMOKE-PLAN-01

Status: `designed_infrastructure_only`; provider calls are not authorized.

This goal defines, but does not execute, a bounded schema smoke for the two
documentation-selected liquidity sources. The future call matrix is fixed at
four calls:

- symbols: `002475.SZ` and `600036.SH`;
- endpoints: Tushare Pro `daily_basic` and Baostock
  `query_history_k_data_plus`;
- at most one call for each provider/symbol pair;
- total call budget four; and
- zero retries under every outcome.

The plan records expected field names and source units. Tushare `free_share`
and `float_share` use ten-thousand-share units, while turnover fields use
percent. Baostock volume uses shares, `turn` uses percent, `tradestatus` uses
the documented trading/suspension enum, and only `adjustflag=2` represents
QFQ in the downstream normalization contract.

Any future executor must stop on authorization, client, credential,
authentication, entitlement, network, rate-limit, provider-service, empty
response, schema, symbol-scope, or row-budget failure. Retries and partial
substitution are forbidden. Persistable observations are restricted to the
allowlisted sanitized metadata shape: call identity, provider and endpoint,
canonical/provider symbol, attempted status, call/retry counts, classified
failure status, observed field names, and observed row count. Raw rows, raw
payloads, exception bodies, credentials, tokens, request headers, and private
logs are forbidden.

The current plan is offline and zero-call: it imports no provider SDK, opens no
network transport, reads no credential, and writes no repository output. A
future live schema smoke requires separate explicit user authorization and a
separate execution goal. This design does not accept provider schemas, create
liquidity evidence, or unlock factor construction, recommendation tiering,
positions, backtests, dashboards, trading, brokers, or production.
