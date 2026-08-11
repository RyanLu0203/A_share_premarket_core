from __future__ import annotations

import io
import json
import subprocess
import sys
import traceback
from pathlib import Path
from urllib.error import HTTPError

import pytest

from ashare_premarket.providers.ifind_http import (
    IFIND_ACCESS_TOKEN_ENV,
    IFIND_BASE_URL,
    IFIND_DATA_MODULES,
    IFIND_NETWORK_ENV,
    IFIND_PROVIDER_ENV,
    IFIND_REFRESH_TOKEN_ENV,
    IfindCredentials,
    IfindHttpClient,
    IfindNoRedirectHandler,
    IfindNetworkPolicy,
    IfindProviderError,
    IfindUrllibTransport,
    ifind_readiness,
)


ROOT = Path(__file__).resolve().parents[1]


def test_ifind_is_network_disabled_by_default_and_never_exposes_token_values() -> None:
    secret = "fixture-secret-never-print"
    readiness = ifind_readiness({IFIND_REFRESH_TOKEN_ENV: secret})
    rendered = json.dumps(readiness, ensure_ascii=False)

    assert readiness["readiness_state"] == "OFFLINE_READY_NETWORK_DISABLED"
    assert readiness["live_access_allowed"] is False
    assert readiness["refresh_token_present"] is True
    assert readiness["token_value_exposed"] is False
    assert secret not in rendered
    assert secret not in repr(IfindCredentials(refresh_token=secret))
    assert secret not in repr(
        IfindHttpClient(credentials=IfindCredentials(refresh_token=secret))
    )


@pytest.mark.parametrize(
    ("environment", "failure_code"),
    [
        ({IFIND_PROVIDER_ENV: "1"}, "IFIND_NETWORK_DISABLED_BY_POLICY"),
        ({IFIND_NETWORK_ENV: "1"}, "IFIND_PROVIDER_DISABLED_BY_POLICY"),
    ],
)
def test_ifind_requires_both_explicit_network_opt_ins(
    environment: dict[str, str], failure_code: str
) -> None:
    client = IfindHttpClient(
        credentials=IfindCredentials(access_token="fixture"),
        policy=IfindNetworkPolicy.from_environment(environment),
        transport=lambda *_args: (200, {}),
    )
    with pytest.raises(IfindProviderError) as exc:
        client.history_quotation(["000333.SZ"], ["close"], "2026-07-01", "2026-07-02")
    assert exc.value.failure_code == failure_code


def test_ifind_refresh_token_is_used_only_for_access_token_exchange() -> None:
    calls: list[tuple[str, dict[str, str], object]] = []

    def transport(url: str, headers: dict[str, str], payload: object, _timeout: float):
        calls.append((url, dict(headers), payload))
        if url.endswith("/get_access_token"):
            return 200, {"data": {"access_token": "short-lived-access"}}
        return 200, {"errorcode": 0, "tables": [{"thscode": ["000333.SZ"]}]}

    client = IfindHttpClient(
        credentials=IfindCredentials(refresh_token="long-lived-refresh"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=transport,
    )
    result = client.history_quotation(
        ["000333.SZ"], ["open", "close"], "2026-07-01", "2026-07-02"
    )

    assert result["errorcode"] == 0
    assert len(calls) == 2
    assert calls[0][0] == f"{IFIND_BASE_URL}/api/v1/get_access_token"
    assert calls[0][1]["refresh_token"] == "long-lived-refresh"
    assert "access_token" not in calls[0][1]
    assert calls[1][1]["access_token"] == "short-lived-access"
    assert "refresh_token" not in calls[1][1]
    assert calls[1][2] == {
        "codes": "000333.SZ",
        "indicators": "open,close",
        "startdate": "2026-07-01",
        "enddate": "2026-07-02",
        "functionpara": {"Fill": "Blank"},
    }


@pytest.mark.parametrize("credential_kind", ["access_token", "refresh_token"])
@pytest.mark.parametrize("token_case", ["control_character", "non_ascii", "oversized"])
def test_ifind_rejects_malformed_credentials_before_transport_without_echoing_values(
    credential_kind: str,
    token_case: str,
) -> None:
    secret = {
        "control_character": "fixture-secret\r\nInjected: yes",
        "non_ascii": "fixture-secret-令牌",
        "oversized": "A" * 8193,
    }[token_case]
    calls = 0

    def transport(*_args):
        nonlocal calls
        calls += 1
        return 200, {}

    client = IfindHttpClient(
        credentials=IfindCredentials(**{credential_kind: secret}),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=transport,
    )
    with pytest.raises(IfindProviderError) as exc:
        client.history_quotation(["000333.SZ"], ["close"], "2026-07-01", "2026-07-02")

    assert exc.value.failure_code == "IFIND_CREDENTIAL_FORMAT_INVALID"
    assert secret not in str(exc.value)
    assert secret not in repr(exc.value)
    assert calls == 0


def test_ifind_rejects_malformed_provider_access_token_before_reuse() -> None:
    secret = "provider-secret\r\nInjected: yes"
    calls = 0

    def transport(*_args):
        nonlocal calls
        calls += 1
        return 200, {"data": {"access_token": secret}}

    client = IfindHttpClient(
        credentials=IfindCredentials(refresh_token="valid-refresh-token"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=transport,
    )
    with pytest.raises(IfindProviderError) as exc:
        client.get_access_token()

    assert exc.value.failure_code == "IFIND_CREDENTIAL_FORMAT_INVALID"
    assert secret not in str(exc.value)
    assert calls == 1


def test_ifind_redirects_are_rejected_before_credentials_can_be_forwarded() -> None:
    handler = IfindNoRedirectHandler()
    assert (
        handler.redirect_request(
            None, None, 302, "Found", {}, "https://example.com/steal"
        )
        is None
    )

    transport = IfindUrllibTransport()
    assert any(
        isinstance(item, IfindNoRedirectHandler) for item in transport._opener.handlers
    )


def test_ifind_request_validation_is_bounded_before_transport() -> None:
    calls = 0

    def transport(*_args):
        nonlocal calls
        calls += 1
        return 200, {}

    client = IfindHttpClient(
        credentials=IfindCredentials(access_token="fixture"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=transport,
    )
    with pytest.raises(IfindProviderError, match="canonical exchange-suffixed"):
        client.history_quotation(["000333"], ["close"], "2026-07-01", "2026-07-02")
    with pytest.raises(IfindProviderError, match="unsupported characters"):
        client.history_quotation(
            ["000333.SZ"], ["close;drop"], "2026-07-01", "2026-07-02"
        )
    with pytest.raises(IfindProviderError, match="start date"):
        client.history_quotation(["000333.SZ"], ["close"], "2026-07-03", "2026-07-02")
    assert calls == 0


def test_ifind_all_approved_endpoints_use_dedicated_bounded_wrappers() -> None:
    calls: list[tuple[str, object]] = []

    def transport(url: str, _headers: dict[str, str], payload: object, _timeout: float):
        calls.append((url, payload))
        return 200, {"errorcode": 0, "tables": [{"time": ["2026-07-01"]}]}

    client = IfindHttpClient(
        credentials=IfindCredentials(access_token="fixture"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=transport,
    )
    assert not hasattr(client, "query")
    client.date_sequence(
        ["000333.SZ"],
        [{"indicator": "ths_close_price_stock", "indiparams": ["", "100", ""]}],
        "2026-07-01",
        "2026-07-02",
    )
    client.data_pool(
        "p03425",
        {"date": "20260701", "blockname": "001005010"},
        ["p03291_f001", "p03291_f002"],
    )
    client.edb(["G009035746"], "2026-07-01", "2026-07-02")
    client.report_query(
        ["000333.SZ"],
        ["901"],
        "2026-07-01",
        "2026-07-02",
        ["reportDate:Y", "thscode:Y", "reportTitle:Y"],
    )
    client.trade_dates("212001", "2026-07-02", offset=-10)

    assert [url.rsplit("/", 1)[-1] for url, _payload in calls] == [
        "date_sequence",
        "data_pool",
        "edb_service",
        "report_query",
        "get_trade_dates",
    ]
    assert calls[0][1] == {
        "codes": "000333.SZ",
        "startdate": "2026-07-01",
        "enddate": "2026-07-02",
        "functionpara": {"Fill": "Blank"},
        "indipara": [
            {"indicator": "ths_close_price_stock", "indiparams": ["", "100", ""]}
        ],
    }
    assert calls[-1][1] == {
        "marketcode": "212001",
        "functionpara": {
            "dateType": "0",
            "period": "D",
            "offset": "-10",
            "dateFormat": "0",
            "output": "sequencedate",
        },
        "startdate": "2026-07-02",
    }


def test_ifind_endpoint_wrappers_reject_unbounded_or_nested_payloads_before_transport() -> (
    None
):
    calls = 0

    def transport(*_args):
        nonlocal calls
        calls += 1
        return 200, {}

    client = IfindHttpClient(
        credentials=IfindCredentials(access_token="fixture"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=transport,
    )
    with pytest.raises(IfindProviderError, match="date span"):
        client.edb(["G009035746"], "2000-01-01", "2026-07-02")
    with pytest.raises(IfindProviderError, match="nested"):
        client.data_pool("p03425", {"date": {"unsafe": "nested"}}, ["p03291_f001"])
    with pytest.raises(IfindProviderError, match="output fields"):
        client.report_query(
            ["000333.SZ"], ["901"], "2026-07-01", "2026-07-02", ["pdfURL:Y;DROP"]
        )
    with pytest.raises(IfindProviderError, match="offset"):
        client.trade_dates("212001", "2026-07-02", offset=5000)
    assert calls == 0


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, "IFIND_AUTH_OR_PERMISSION_DENIED"),
        (403, "IFIND_AUTH_OR_PERMISSION_DENIED"),
        (429, "IFIND_RATE_LIMITED"),
        (503, "IFIND_PROVIDER_SERVER_ERROR"),
    ],
)
def test_ifind_http_failures_have_stable_safe_codes(status: int, expected: str) -> None:
    client = IfindHttpClient(
        credentials=IfindCredentials(access_token="fixture-secret"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=lambda *_args: (status, {"message": "unsafe provider detail"}),
    )
    with pytest.raises(IfindProviderError) as exc:
        client.history_quotation(["000333.SZ"], ["close"], "2026-07-01", "2026-07-02")
    assert exc.value.failure_code == expected
    assert "fixture-secret" not in str(exc.value)
    assert "unsafe provider detail" not in str(exc.value)


@pytest.mark.parametrize(
    ("status", "body", "expected"),
    [
        (401, b"", "IFIND_AUTH_OR_PERMISSION_DENIED"),
        (429, b"<html>gateway</html>", "IFIND_RATE_LIMITED"),
        (503, b"upstream unavailable", "IFIND_PROVIDER_SERVER_ERROR"),
    ],
)
def test_ifind_default_transport_preserves_http_failure_taxonomy_for_non_json_errors(
    status: int,
    body: bytes,
    expected: str,
) -> None:
    transport = IfindUrllibTransport()

    class FailingOpener:
        def open(self, request, timeout):
            raise HTTPError(request.full_url, status, "failure", {}, io.BytesIO(body))

    transport._opener = FailingOpener()
    client = IfindHttpClient(
        credentials=IfindCredentials(access_token="fixture"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=transport.post_json,
    )
    with pytest.raises(IfindProviderError) as exc:
        client.history_quotation(["000333.SZ"], ["close"], "2026-07-01", "2026-07-02")
    assert exc.value.failure_code == expected


@pytest.mark.parametrize(
    "transport_error",
    [
        ValueError("Invalid header value b'fixture-secret-never-echo'"),
        UnicodeEncodeError("ascii", "令", 0, 1, "ordinal not in range"),
    ],
)
def test_ifind_transport_converts_header_encoding_failures_to_safe_errors(
    transport_error: Exception,
) -> None:
    secret = "fixture-secret-never-echo"
    transport = IfindUrllibTransport()

    class FailingOpener:
        def open(self, _request, timeout):
            raise transport_error

    transport._opener = FailingOpener()
    with pytest.raises(IfindProviderError) as exc:
        transport.post_json(
            f"{IFIND_BASE_URL}/api/v1/cmd_history_quotation",
            {"Content-Type": "application/json", "access_token": "valid-access-token"},
            {"codes": "000333.SZ"},
            20.0,
        )

    assert exc.value.failure_code == "IFIND_CREDENTIAL_FORMAT_INVALID"
    assert secret not in str(exc.value)
    assert secret not in repr(exc.value)
    rendered_traceback = "".join(
        traceback.format_exception(type(exc.value), exc.value, exc.value.__traceback__)
    )
    assert secret not in rendered_traceback


def test_ifind_provider_application_error_does_not_echo_vendor_content() -> None:
    unsafe = "fixture-vendor-error-content-never-echo"
    client = IfindHttpClient(
        credentials=IfindCredentials(access_token="fixture-secret"),
        policy=IfindNetworkPolicy(network_opt_in=True, provider_opt_in=True),
        transport=lambda *_args: (200, {"errorcode": unsafe}),
    )
    with pytest.raises(IfindProviderError) as exc:
        client.history_quotation(["000333.SZ"], ["close"], "2026-07-01", "2026-07-02")
    assert exc.value.failure_code == "IFIND_PROVIDER_RESPONSE_ERROR"
    assert unsafe not in str(exc.value)


def test_ifind_contract_covers_data_foundation_and_preserves_execution_locks() -> None:
    contract = json.loads(
        (
            ROOT / "configs/providers/ifind_ai_financial_data_service_contract.yaml"
        ).read_text(encoding="utf-8")
    )
    assert contract["provider_name"] == "同花顺 iFinD"
    assert contract["product_name"] == "AI 金融数据服务"
    assert contract["credential_policy"]["persist_tokens"] is False
    assert contract["storage_policy"]["raw_payload_commit"] == "forbidden"
    assert len(contract["data_modules"]) == len(IFIND_DATA_MODULES) == 7
    assert all(contract["locked_boundaries"].values())


def test_ifind_probe_default_mode_is_offline_and_secret_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "fixture-secret-never-echo"
    environment = {
        **__import__("os").environ,
        IFIND_REFRESH_TOKEN_ENV: secret,
    }
    environment.pop(IFIND_NETWORK_ENV, None)
    environment.pop(IFIND_PROVIDER_ENV, None)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_ifind_provider_probe.py")],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert secret not in result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["readiness"]["live_access_allowed"] is False
    assert payload["readiness"]["token_value_exposed"] is False


def test_ifind_live_auth_probe_requires_refresh_exchange_and_never_accepts_access_only() -> (
    None
):
    secret = "fixture-access-token-must-not-be-echoed"
    environment = {
        **__import__("os").environ,
        IFIND_ACCESS_TOKEN_ENV: secret,
        IFIND_NETWORK_ENV: "1",
        IFIND_PROVIDER_ENV: "1",
    }
    environment.pop(IFIND_REFRESH_TOKEN_ENV, None)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_ifind_provider_probe.py"),
            "--live-auth",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert secret not in result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    assert payload["failure_code"] == "IFIND_REFRESH_TOKEN_REQUIRED_FOR_AUTH_PROBE"
    assert payload["readiness"]["live_access_allowed"] is True
