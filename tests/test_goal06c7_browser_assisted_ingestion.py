from __future__ import annotations

import ashare_premarket.providers.provider_ladder as ladder
from ashare_premarket.providers.browser_assisted_provider import BrowserFetchResult


def test_browser_domain_access_only_is_not_structured_ingestion_success() -> None:
    result = BrowserFetchResult(
        key="sample",
        url="https://push2his.eastmoney.com/sample",
        status="PASS",
        content_type="text/html",
        body_text="<html>Eastmoney</html>",
    )
    assert ladder._browser_failure_class(result) == "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY"


def test_browser_structured_rows_receive_solved_tag(monkeypatch, tmp_path) -> None:
    url_rows = {
        "data": {
            "klines": [
                "2023-01-01,10,11,12,9,1000,100000",
                "2023-01-02,11,12,13,10,1001,100001",
            ]
        }
    }
    body = __import__("json").dumps(url_rows)

    def fake_fetch(urls):
        return [
            BrowserFetchResult(
                key=urls[0][0],
                url=urls[0][1],
                status="PASS",
                http_status="200",
                content_type="application/json",
                body_text=body,
            )
        ]

    monkeypatch.setattr(ladder, "_fetch_direct", lambda url, data_role, symbol: ([], ladder._attempt("akshare", "akshare_direct", "stock_zh_a_hist", data_role, "push2his.eastmoney.com", "FAIL", "BROWSER_NET_EMPTY_RESPONSE", "network_transport")))
    monkeypatch.setattr(ladder, "browser_domain_allowed", lambda root, url: True)
    monkeypatch.setattr(ladder, "fetch_urls_with_browser", fake_fetch)
    monkeypatch.setattr(ladder, "_local_rows", lambda root, data_role, symbol: [])
    rows, events = ladder._fetch_role(tmp_path, "stock_ohlcv_daily", "600036.SH", "20230101", "20230131", browser_enabled=True)
    assert len(rows) == 2
    browser_event = [event for event in events if event["provider_mode"] == "browser_assisted_optional"][0]
    assert browser_event["primary_failure_class"] == "BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED"
    assert browser_event["schema_valid"] is True
