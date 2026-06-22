# CloakBrowser Reference Ingestion Probe

Status: `PASS_WITH_WARNINGS`
Reference repo: `CloakHQ/CloakBrowser`
Reference commit inspected: `29679a73bfc64dfb6f97094615741a0ee8022a55`
Reference pattern: `optional_drop_in_browser_runtime_probe`
Network opt-in: `true`
Browser opt-in: `true`
Browser dependency status: `AVAILABLE`
Missing dependencies: ``
Problem rows inspected: `3`
Browser probes attempted: `3`
Domain-access solved by reference: `2`
Ingestion solved by reference: `1`
Remaining unsolved for source-backed ingestion: `2`
Raw HTML stored: `false`
Raw payload stored: `false`
Default AKShare provider path changed: `false`
GOAL-06D allowed to proceed: `false`

## Interpretation
At least one provider access problem produced structured-data evidence through the CloakBrowser reference path; only those rows are tagged as ingestion solved.

## Tag Counts
- `CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_EMPTY_RESPONSE`: `1`
- `SOLVED_BY_CLOAKBROWSER_REFERENCE_DOMAIN_ACCESS_ONLY`: `1`
- `SOLVED_BY_CLOAKBROWSER_REFERENCE_INGESTION`: `1`

## Problem Tags
- `cloakbrowser_reference-0001` `index_zh_a_hist`: `SOLVED_BY_CLOAKBROWSER_REFERENCE_INGESTION`; remaining ``; notes: HTTP 200; body inspected in memory only
- `cloakbrowser_reference-0002` `stock_info_a_code_name`: `SOLVED_BY_CLOAKBROWSER_REFERENCE_DOMAIN_ACCESS_ONLY`; remaining `HTML_RETURNED_INSTEAD_OF_DATA`; notes: HTTP 200; body inspected in memory only
- `cloakbrowser_reference-0003` `stock_zh_a_spot_em`: `CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_EMPTY_RESPONSE`; remaining `BROWSER_NET_EMPTY_RESPONSE`; notes: browser probe exception: Error: Page.goto: net::ERR_EMPTY_RESPONSE at https://82.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m%3A0+t%3A6%2Cm%3A0+t%3A80%2Cm%3A1+t%3A
