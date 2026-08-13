# 同花顺 iFinD AI 金融数据服务接入说明

> 2026-08-12 live checkpoint：S0 已通过 7/7 服务与个人/试用版 35/35 个
> entitlement 工具及 input schema。完整审阅目录仍为 36，企业版专属
> `edb:search_edb` 标记为 `UNAVAILABLE_BY_PLAN`。早期 S1 暴露的代码范围、供应商
> 代码/简称反放及查询合同问题均已离线、fail-closed 修复。PR #49 合并部署后，
> 一次有界 S1 对立讯精密和亨通光电各调用一次且未重试；两条单行摘要均通过证券
> 范围、公司身份和响应结构校验。call-plan v2 将其接纳为身份验收元数据：本地
> `observed_at` 仅表示验收观察时间，provider `available_at` 明确未知，canonical
> 行仍为 0。其后一个授权 S2 批次在首个立讯 `get_stock_info` 调用因通用响应
> schema 不匹配而停止：1/4 次、零重试、零接纳行。

> S2 离线基础按供应商 `ifind-finance-data-1.3.0` 股票参考固定为
> `get_stock_info` 与 `get_stock_performance` 各调用两只股票一次，共四次、零
> 重试。2026-08-13 已离线完成分层、metadata-only 响应诊断和未来 accepted
> bundle 的严格读门；没有再次调用供应商、读取钥匙串或接纳数据。旧失败没有
> 足够形态元数据可供复原，下一次重试仍需单独授权。

本文定义项目对已购买的同花顺 iFinD「AI 金融数据服务」的安全接入、数据分层、落盘和验收边界。iFinD 在本项目中的定位是付费专业金融数据源，用于补全证券主数据、行情、PIT 财务与估值、行业、公告元数据、宏观和市场结构证据；它不是自然语言选股器、推荐系统或交易执行入口。

用户实际购买的是 iFinD **MCP/API Key** 产品。项目因此以官方
Streamable HTTP MCP 通道为主：固定基址为
`https://api-mcp.51ifind.com:8643/ds-mcp-servers`，覆盖 A 股、基金、
宏观、新闻公告、债券、港美股和指数板块七个服务。`quantapi.51ifind.com`
HTTPS 适配器保留为可选第二通道，只有账号另有 QuantAPI 权益时才启用。

供应商 `ifind-finance-data` 1.3.0 Skill 只作为工具目录和协议证据，不会原样
安装或执行：其 Python 示例关闭 TLS 证书校验，配置文件明文保存密钥，且包
目录权限过宽。项目重写了受治理客户端，强制 TLS、固定域名/端口/路径、禁止
重定向和代理继承、限制请求/响应、默认每秒最多两次请求，并将自由文本结果
视为非可信、非 canonical 数据。

官方参考：

- [数据接口文档](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/)
- [部署与认证](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/deploy.html)
- [HTTP / Python 示例](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/example.html)
- [iFinD 产品主页](https://www.51ifind.com)
- 用户从 iFinD MCP 控制台下载的 `ifind-finance-data` 1.3.0 Skill 与七服务配置

## 凭据安全

先前在聊天和生成 RTF 中暴露的旧凭据已被项目永久禁用，不得用于任何探针、
开发、测试或数据请求。用户已报告完成轮换；这一报告不等于外部 MCP 认证已经
通过。本文和项目代码都不得记录、复述或提交任何新旧凭据值。

新 MCP API Key 首选从 macOS 钥匙串读取，只在进程内存中使用。首选钥匙串
引用为 Generic Password：服务 `AsharePremarket-iFinD-API-Key`、账号
`ifind`；旧式 Internet Password（账号 `ifind`、网站
`mcp.51ifind.com`）仅作兼容回退。可选环境变量仅用于经批准的无钥匙串运行
环境：

| 环境变量 | 作用 | 默认状态 |
|---|---|---|
| `ASHARE_ALLOW_NETWORK_INGESTION` | 项目级金融网络访问总开关 | 未开启 |
| `ASHARE_ALLOW_IFIND` | iFinD provider 专属开关 | 未开启 |
| `ASHARE_ALLOW_IFIND_MCP` | MCP 通道专属开关 | 未开启 |
| `ASHARE_ALLOW_IFIND_MCP_DATA_CALLS` | 通过握手与 schema 验收后的数据调用专属开关 | 未开启 |
| `IFIND_MCP_API_KEY` | 无钥匙串环境的可选 MCP API Key | 未设置 |
| `IFIND_ACCESS_TOKEN` / `IFIND_REFRESH_TOKEN` | 可选 QuantAPI 第二通道 | 未设置 |

任何 MCP live 握手必须同时满足前三个开关；`tools/call` 数据调用还必须满足
第四个 `ASHARE_ALLOW_IFIND_MCP_DATA_CALLS=1`。缺少任一适用开关时均失败
关闭。API Key 按供应商 1.3.0 合同原样写入 `Authorization` 请求头，不添加
`Bearer` 前缀。密钥不得写入项目配置、manifest、命令参数、终端输出、日志、
测试 fixture、Git 历史或 Dashboard 响应。Dashboard 只展示凭据交付策略，
不读取密钥、检测密钥是否存在或显示任何密钥派生值。

## 默认离线与网络边界

- 默认状态是 `OFFLINE_READY_NETWORK_DISABLED`，允许检查合同、模块目录和
  凭据交付策略，但不读取钥匙串、判断密钥是否存在或访问网络。
- live MCP 访问需要 `ASHARE_ALLOW_NETWORK_INGESTION=1`、
  `ASHARE_ALLOW_IFIND=1` 与 `ASHARE_ALLOW_IFIND_MCP=1` 三重显式授权。
- 只允许 `api-mcp.51ifind.com:8643` 的七条精确路径；系统代理继承与重定向
  被禁用，TLS 证书验证保持开启。
- 协议顺序固定为 `initialize` → `notifications/initialized` → `tools/list` →
  经显式 schema 校验且第四开关获准后的 `tools/call`，会话头为
  `Mcp-Session-Id`。
- 请求体最多 64 KiB、响应最多 8 MiB、超时不超过 60 秒，不自动重试；在
  未核验购买权益前按免费边界每秒最多 2 次请求。
- 自然语言查询最多 1,000 字符；高频行情主体和指标各最多 10 个，周期仅限
  1/3/5/10/15/30/60 分钟；新闻单次最多 20 条。
- 只有 `structuredContent` 或单一、可严格解析为 JSON 对象的文本可进入后续
  schema 验收；普通自然语言、Markdown、新闻/公告文字不得成为 canonical 数据。
- 认证探针不等于数据模块验收，更不等于将 iFinD 提升为 canonical provider。

## 七个数据模块及优先级

| 优先级 | 模块 | MCP 服务与工具 | 主要证据 | Dashboard 基础表面 |
|---|---|---|---|---|
| P0 | `security_master` | `stock`: `get_stock_info`、`get_stock_shareholders`、`get_stock_events` | 上市日期、交易状态、总股本、流通股本、自由流通股本、行业分类及其生效版本 | 股票身份与资本结构 |
| P0 | `daily_market_and_calendar` | `stock/index`: `get_stock_performance`、`stock_highfreq_quotes`、`index_data` | 日线使用 `trade_date + symbol`；交易日历继续使用现有受治理日历或另行授权的 QuantAPI；保留 OHLCV、成交额、换手率、复权口径和数据截止时间 | 行情与 Provider Health |
| P0 | `pit_fundamentals_and_valuation` | `stock`: `get_stock_financials`、`get_stock_summary` | PE、PB、PS、ROE、营收、利润、负债率、现金流，以及报告期、公告日、修订时点和可用时点 | 股票基本面 |
| P1 | `industry_and_constituents` | `stock/index`: `search_stocks`、`sector_data` | 行业代码、分类版本、历史成分、生效与失效日期；禁止用当前成分回填历史 | 市场环境与股票身份 |
| P1 | `corporate_events_and_announcements` | `stock/news`: `get_stock_events`、`search_notice` | 公告时间、类型、标题、证券代码和报告期，仅保留元数据 | 公司事件上下文 |
| P1 | `macro_and_edb` | `edb`: `search_edb`、`get_edb_data` | 宏观指标、观测期、发布日期、修订标识、单位和数值 | 市场环境 |
| P1 | `market_structure_crosscheck` | `stock/index`: `get_stock_performance`、`get_risk_indicators`、`index_data`、`sector_data` | 两融、北向、市场宽度、资金流、自由流通市值及供应商定义版本 | Provider Health 与研究就绪度 |

P0 必须先完成 entitlement、字段映射、PIT、覆盖和缺失率验收。P1 用于补足历史分类、事件、宏观和交叉验证；P1 缺失不得由推断值、当前值回填或其他供应商逐行拼接掩盖。

## 双股验收队列与 Workspace 浏览边界

首批有界验收证券固定为立讯精密 `002475.SZ` 和亨通光电 `600487.SH`。
Workspace 将“证券可浏览”与“参考组合成员资格”分开：两只证券都可进入股票
浏览接口和页面，但页面可见不代表已进入参考组合，也不代表已生成风险、推荐
或持仓结论；组合成员状态必须单独展示。

- `002475.SZ` 已有现有 committed Provider02B 的 120 个交易日证据，可用于
  只读基础行情回放；这不是 iFinD live 接纳结果。
- `600487.SH` 当前只有受治理的试点身份，尚无已接纳的 iFinD 行情、财务或
  研究数据。相关页面必须显示空状态，不得用推断、零值或另一证券的数据填充。
- iFinD 数据只有通过外部认证、工具 schema、固定调用预算、PIT、覆盖和
  normalization 验收后，才能进入这两只证券的规范化只读模型。

### S2 固定数据合同

- 请求范围固定为 `002475.SZ`、`600487.SH`，工具固定为
  `get_stock_info`、`get_stock_performance`；调用者不能提供 query、工具或
  symbol，调用预算固定为四次且不重试。
- `get_stock_info` 每股必须返回一行证券代码、简称、数据日期、带时区的供应商
  可用时间、上市日期、交易状态、总股本和流通股本；两个股本单位都必须显式为
  `股`，不接受把 `万股`、`手` 或未声明单位的数值直接映射为 canonical 股数。
- `get_stock_performance` 每股必须恰好返回最近 120 个已完成交易日；日期集合
  必须与现有受治理交易日历完全一致，复权必须明确为 QFQ，成交量/成交额/换手率
  口径必须分别显式为 `股`、`元`、`百分比/%`，并带统一、带时区的供应商可用
  时间。不能用本地抓取时间替代。
- 任意跨股票行、列缺失、行数漂移、日历漂移、非 QFQ、无时区或可用时间晚于
  decision cutoff 都进入拒绝/隔离，不写外部 normalized bundle。
- Workspace 展示离线合同、固定工具/预算、最近一次 allowlisted S2 结果及未来
  metadata-only 诊断字段；`s2_live_calls_authorized=false`、
  `s2_provider_schema_accepted=false`、canonical iFinD 行数仍为 0。旧失败的
  stage/reason/shape 显示为未捕获，而不是根据通用失败码猜测。

### S2 离线响应诊断与 accepted bundle 读门

旧状态只保留通用失败码，无法证明失败是在 JSON-RPC、MCP result、供应商
envelope、Markdown 还是 S2 列选择；项目不会从缺失证据猜测原因。未来失败只
保留固定阶段/原因、受限计数、固定必填列存在性和不含单元格值的结构指纹，
不会保存正文、表格值、标题、body hash、异常文本、路径或凭据。

未来完整 S2 bundle 还必须由 PASS 状态同时锚定 bundle id 与 manifest SHA-256，
并经只读层重新校验权限、symlink/路径、四文件/242 行、文件与规范化校验和、
schema/重算后的 request/license lineage、主键、数值域、双股范围、受治理的精确
120 个交易日、单位、单一供应商可用时点、QFQ 和 PIT。任一失败整包返回零行；
live evidence 不与 Provider02B 逐行混用，也不
进入 immutable replay。完整数据质量结论见
[IFIND_S2_RESPONSE_CONTRACT_DIAGNOSIS.md](IFIND_S2_RESPONSE_CONTRACT_DIAGNOSIS.md)。

## 规范化与本地存储

规范化输出使用 `ifind-normalized-v1`，每行保留 `provider_id`、`source_function`、`request_digest`、`schema_version`、`available_at`、`license_storage_class`、`quality_flags` 和批次校验和。每个模块按自己的 canonical grain 和主键排序、去重，并在落盘前执行必填字段、日期、数值、OHLC 和 PIT cutoff 校验。

付费规范化数据只能写入仓库之外的本地数据根：

```text
ASHARE_PREMARKET_DATA_ROOT/
  normalized/
    ifind/
      <module_id>/
        <immutable_bundle_id>/
          rows.jsonl
          manifest.json
```

bundle ID 不可覆盖。manifest 记录 schema 版本、请求摘要、行数、覆盖范围、规范化校验和和 `rows.jsonl` SHA-256；许可存储类别为 `paid_provider_local_only`。

`ASHARE_PREMARKET_DATA_ROOT` 必须显式设置；付费 bundle 不允许使用文档
默认根。iFinD 目录使用 `0700`、数据和 manifest 文件使用 `0600`。无时区
时间戳默认拒绝；只有在字段语义核验后，调用方才可明确声明
`Asia/Shanghai`，随后统一转换为 UTC。
公告日、报告期、交易日等 date-only 字段则始终在 `Asia/Shanghai` 业务日
口径下与 `available_at` 和 `decision_cutoff` 比较，避免 UTC 午夜边界造成
错误拒绝或错误接受。

Git 中禁止出现：

- 原始 iFinD 响应或完整付费数据集；
- 任何访问令牌、刷新令牌、认证头或可恢复凭据；
- 完整公告正文、研报全文或新闻全文；
- 本地 bundle、数据库、Parquet、SQLite、DuckDB、缓存、日志和私有运行证据；
- 由付费数据直接导出的可重建全量镜像。

Git 仅允许提交有界、脱敏的 schema、覆盖率、缺失率、失败分类、manifest 摘要和审计结论；提交前必须通过许可证边界和 secret scan。

## 安全探针

默认离线检查合同和 readiness，不发起网络请求：

```bash
python scripts/run_ifind_mcp_probe.py
```

只有用户确认轮换后的凭据已通过批准的注入路径交付，并且明确授权本次认证
检查后，才可运行单服务握手探针：

```bash
ASHARE_ALLOW_NETWORK_INGESTION=1 ASHARE_ALLOW_IFIND=1 \
ASHARE_ALLOW_IFIND_MCP=1 \
python scripts/run_ifind_mcp_probe.py --live-handshake --server stock
```

`--live-handshake` 只执行初始化和 `tools/list`，不执行 `tools/call`，不抓取
金融数据，不写原始响应，不打印或持久化密钥。若认证、权限、TLS、网络、
限频、协议或响应结构失败，脚本只返回稳定失败码和非敏感状态。可选 QuantAPI
第二通道仍可用 `python scripts/run_ifind_provider_probe.py` 做纯离线合同检查。

如需让本地 Data Quality / Provider Health 显示最近一次外部探针结果，可追加
`--write-local-status`。它只在被 Git 忽略的 `outputs/local/ifind` 中写入
`0600` 权限的状态、失败码、HTTP 状态、工具数量和 schema 验收布尔值；认证头、
Keychain 值、供应商响应体和原始 schema 均不写入。

双股分阶段计划可先做完全离线校验：

```bash
python scripts/run_ifind_mcp_dual_stock_acceptance.py
```

`--live-handshake` 会在同一次受控运行内核对全部七个服务、完整审阅目录与当前
套餐 entitlement，只输出工具名与 input schema 的 SHA-256。S1 数据探针还需
独立第四开关和显式带时区的 `--decision-timestamp`；它固定只调用立讯精密和
亨通光电各一次 `get_stock_summary`。只有两股的范围、身份与结构全部通过时，
才返回 `S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED`；它仍明确
`canonical_accepted=false`，不会打印或保存供应商原文。旧的精确 PIT-blocked
本地状态可在部署 v2 后使用 `--reclassify-existing-s1-status` 离线迁移。

截至 2026-08-12，受治理客户端已完成外部认证和 S0：7/7 服务、35/35 当前
entitlement 工具与 live schema 通过。`search_edb` 的缺失由官方套餐范围解释为
企业版专属。早期 S1 的范围、代码/简称反放和查询合同问题均已 fail-closed 修复。
PR #49 合并并部署到 `6e5fbfa` 后，一次授权运行完成同次 S0，并固定调用立讯与
亨通各一次；两条摘要各形成一张表、一行身份数据，证券范围、配置公司名和结构
均通过。供应商摘要不提供可审计的 provider `available_at`。call-plan v2 因此只
将两条摘要验收为 `acceptance_metadata_only`：本地采集时间标记为 `observed_at`
验收元数据，provider `available_at` 保持未知，零 canonical 行、无 raw 落盘、无
重试。只有原本精确满足两次调用、无失败证券、S0/schema 通过的本地状态可离线
迁移；S2 仍需单独授权。

S2 已有默认关闭的 fail-closed live runner。它在同一客户端会话重新完成七服务
S0，再固定执行两只股票各一次 `get_stock_info` 和 `get_stock_performance`，最多
四次、零重试。只有两个证券主数据行和 240 个严格匹配治理日历的 QFQ 日线行
全部通过显式 supplier `available_at` 与 PIT 校验，才会原子写入外部付费数据根；
任何首个失败都会停止且不保留 partial/raw。所有 S2 本地状态均为凭据安全白名单。
所有者已授权部署后的这一批次；本段代码变更本身未发起 provider call。

PR #54 部署到 `f7ebbe2` 后，这一批次已执行。同会话 S0 再次通过 7/7 服务和
35/35 entitlement schema；第一个且唯一的 `002475.SZ:get_stock_info` 返回未
匹配审核后的响应结构，状态为 `IFIND_MCP_RESPONSE_SCHEMA_MISMATCH`。执行器在
1/4 次时零重试停止，未调用亨通光电或任一行情工具，未写 raw、normalized、
bundle 或 canonical 数据。再次调用不在本批授权内，必须先离线诊断并重新授权。

## 分阶段验收

### 阶段 0：凭据与合同

- 保持旧暴露凭据永久禁用；记录用户已报告完成轮换，并将受治理 S0 外部认证
  状态保持为已验收；
- 默认离线探针通过；
- 新 MCP Key 只存在于批准的 macOS 钥匙串或一次性进程环境；
- 三个握手 opt-in 与第四个数据调用 opt-in 默认关闭；
- 仓库、Git 历史、日志和运行输出的 secret scan 通过。

### 阶段 1：订阅权限和字段目录

- 对七个 MCP 服务分别执行 `initialize` 和 `tools/list`，核对供应商 1.3.0
  文档化的 36 个工具及实际账号 entitlement；
- 用官方资料和实际账号确认指标、历史深度、频率、限额和缓存/派生许可；
- 为七个模块建立字段、单位、币种、复权、发布日期、修订和供应商定义映射；
- 未授权字段明确标记 `UNAVAILABLE`，不得推断或零填充。

### 阶段 2：有界 live smoke test

- 先通过握手与工具目录探针，再对单一服务、单一工具、极小股票/日期/指标
  范围执行独立的 `tools/call` smoke test；
- `tools/call` 只有在实时 input schema 指纹与语义、固定双股调用计划和请求
  预算均通过后，才可单独开启第四数据调用开关；
- 验证失败分类、限频、超时、schema、唯一键、PIT 和令牌不落盘；
- smoke 行不得直接成为正式研究面板或 canonical 每日刷新证据。

### 阶段 3：P0 数据模块

- 完成证券主数据、日线与交易日历、PIT 财务与估值的规范化 bundle；
- 通过覆盖率、缺失率、单位、复权、公告日、修订版本和 `available_at <= decision_cutoff` 审计；
- 与现有受治理来源完成交叉核验，差异必须解释或隔离，不得平均。

### 阶段 4：P1 数据模块

- 完成历史行业成分、公告元数据、宏观 EDB 和市场结构交叉验证；
- 验证历史成员关系、发布时间、修订策略和供应商定义版本；
- 公告只保留元数据，全文不进入 Git 或 Dashboard 数据合同。

### 阶段 5：Dashboard 基础读模型

- Dashboard 只读取规范化、已校验的本地读模型，不依赖原始响应或令牌；
- 展示数据日期、来源函数、覆盖、缺失、PIT、校验和和失败原因；
- 缺失证据保持 `N/A / UNAVAILABLE`，浏览器不得计算研究结论；
- API 保持 GET-only，不增加写入、推荐、持仓、订单或 broker 路径。

### 阶段 6：数据证据扩展验收

以下合同闸门必须全部通过或有明确隔离结论：凭据轮换、entitlement 目录、有界 live smoke test、失败分类、schema 映射、PIT 与修订、覆盖与缺失、跨供应商核验、Dashboard 无原始依赖、secret scan。随后才可生成受治理的扩展数据证据和独立 readiness report。

## Research 解锁条件

iFinD 接入、认证成功、Dashboard 可展示或数据量扩大，都不会自动解锁 research。只有同时满足以下条件，Main Codex 才可提出新的显式 research goal：

1. 所需 P0 和选定 P1 模块已有不可变规范化 bundle、manifest、校验和与许可审计；
2. PIT、发布日期、修订版本、复权、历史成分、覆盖和缺失率审计通过；
3. 跨供应商差异已通过、解释或隔离，且不存在静默混源；
4. Dashboard 基础模块已基于规范化读模型完成并保持只读、非行动化；
5. 数据扩展 readiness report 为 `PASS` 或可接受的 `PASS_WITH_WARNINGS`；
6. `configs/project/workflow_status.csv`、项目状态、迭代日志、README 和架构文档按晋级规则同步；
7. 用户对新的 research goal 作出明确批准。

Research 获准后仍必须先重跑既有特征、泄漏、walk-forward、稳定性和因子就绪度评估。`ready_factor_count` 不得因购买数据或接入成功而人为调整；Recommendation Tiering、目标价、实际持仓、权重、订单、broker、交易和生产写入仍保持锁定，除非未来独立闸门和用户明确批准。
