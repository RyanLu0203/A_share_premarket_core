from __future__ import annotations

import json
from pathlib import Path

import pytest

from ashare_premarket.ops import observation_basket
from ashare_premarket.providers.akshare_provider import ProviderResult
from ashare_premarket.providers.provider_attempt_log import make_attempt


def test_observation_refresh_writes_only_sanitized_source_backed_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    primary = ProviderResult(
        rows=[
            {"trade_date": "2026-07-09", "symbol": "002475.SZ", "close": 10.0},
            {"trade_date": "2026-07-10", "symbol": "002475.SZ", "close": 11.0},
        ],
        attempt=make_attempt("akshare", "stock_zh_a_hist", status="PASS", failure_class="PROVIDER_OK"),
    )
    monkeypatch.setattr(observation_basket, "load_stock_ohlcv_daily", lambda *_args, **_kwargs: primary)

    payload = observation_basket.refresh_observation_basket(
        tmp_path,
        ["002475.SZ"],
        "2026-07-09",
        "2026-07-10",
        allow_network=True,
    )

    row = payload["rows"][0]
    assert row["close"] == 11.0
    assert row["return_1d"] == pytest.approx(0.1)
    assert row["observation_status"] == "AVAILABLE"
    assert payload["positions_created"] is False
    assert payload["recommendations_created"] is False
    written = json.loads((tmp_path / observation_basket.OBSERVATION_EVIDENCE).read_text(encoding="utf-8"))
    assert written["rows"][0]["selected_provider"] == "akshare"
