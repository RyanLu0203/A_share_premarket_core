from __future__ import annotations

import csv
import hashlib
import ast
import json
from pathlib import Path

import pytest

from ashare_premarket.providers.liquidity_external_handoff import (
    MANIFEST,
    LiquidityHandoffError,
    audit_goal,
    run_goal,
    validate_candidate_bundle_file,
    validate_schema_observation_file,
)
from ashare_premarket.providers.liquidity_schema_smoke_plan import schema_smoke_calls


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/ashare_premarket/providers/liquidity_external_handoff.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_candidate_bundle(path: Path, count: int = 100) -> None:
    fields = [
        "symbol",
        "exchange",
        "security_type",
        "listing_status",
        "source_id",
        "available_at",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for index in range(count):
            writer.writerow(
                {
                    "symbol": f"600{index:03d}.SH",
                    "exchange": "SH",
                    "security_type": "A_share",
                    "listing_status": "listed",
                    "source_id": "synthetic_owner_bundle",
                    "available_at": "2026-08-28T18:00:00+08:00",
                }
            )


def _schema_observations() -> list[dict[str, object]]:
    rows = []
    for call in schema_smoke_calls():
        rows.append(
            {
                "call_id": call["call_id"],
                "provider": call["provider"],
                "endpoint": call["endpoint"],
                "canonical_symbol": call["canonical_symbol"],
                "provider_symbol": call["provider_symbol"],
                "attempted": True,
                "call_count": 1,
                "retry_count": 0,
                "status": "PASS",
                "failure_code": "NONE",
                "observed_field_names": list(call["expected_fields"]),
                "observed_row_count": 1,
            }
        )
    return rows


def test_accepts_external_checksummed_candidate_bundle(tmp_path: Path) -> None:
    path = tmp_path / "candidate_bundle.csv"
    _write_candidate_bundle(path)
    decision = validate_candidate_bundle_file(
        path.resolve(),
        expected_sha256=_sha256(path),
        source_class="owner_supplied_governed_bundle",
        decision_cutoff="2026-08-29T08:00:00+08:00",
        repository_root=ROOT,
    )
    assert decision.status == "PASS"
    assert decision.accepted_symbol_count == 100
    assert not decision.provider_calls_performed


def test_candidate_bundle_rejects_checksum_header_and_repo_path(tmp_path: Path) -> None:
    path = tmp_path / "candidate_bundle.csv"
    _write_candidate_bundle(path)
    with pytest.raises(LiquidityHandoffError, match="CHECKSUM_MISMATCH"):
        validate_candidate_bundle_file(
            path.resolve(),
            expected_sha256="0" * 64,
            source_class="owner_supplied_governed_bundle",
            decision_cutoff="2026-08-29T08:00:00+08:00",
            repository_root=ROOT,
        )

    wrong_header = tmp_path / "wrong_header.csv"
    wrong_header.write_text("symbol,future_return\n600000.SH,1\n", encoding="utf-8")
    with pytest.raises(LiquidityHandoffError, match="HEADER_MISMATCH"):
        validate_candidate_bundle_file(
            wrong_header.resolve(),
            expected_sha256=_sha256(wrong_header),
            source_class="owner_supplied_governed_bundle",
            decision_cutoff="2026-08-29T08:00:00+08:00",
            repository_root=ROOT,
        )
    with pytest.raises(LiquidityHandoffError, match="TRACKED_REPOSITORY_PATH_FORBIDDEN"):
        validate_candidate_bundle_file(
            (ROOT / "configs/research/liquidity_candidate_bundle_template.csv").resolve(),
            expected_sha256=_sha256(
                ROOT / "configs/research/liquidity_candidate_bundle_template.csv"
            ),
            source_class="owner_supplied_governed_bundle",
            decision_cutoff="2026-08-29T08:00:00+08:00",
            repository_root=ROOT,
        )


def test_accepts_exact_sanitized_schema_observation_handoff(tmp_path: Path) -> None:
    path = tmp_path / "schema_observations.json"
    path.write_text(json.dumps(_schema_observations()), encoding="utf-8")
    result = validate_schema_observation_file(
        path.resolve(),
        expected_sha256=_sha256(path),
        repository_root=ROOT,
    )
    assert result["status"] == "PASS_REVIEW_ELIGIBLE_PROVENANCE_UNVERIFIED"
    assert result["observation_count"] == 4
    assert not result["live_schema_verified"]
    assert not result["provider_calls_authorized"]


@pytest.mark.parametrize("mutation", ["raw_value", "retry", "missing_call"])
def test_schema_observation_handoff_fails_closed(
    tmp_path: Path, mutation: str
) -> None:
    rows = _schema_observations()
    if mutation == "raw_value":
        rows[0]["raw_value"] = "forbidden"
    elif mutation == "retry":
        rows[0]["retry_count"] = 1
    else:
        rows.pop()
    path = tmp_path / f"{mutation}.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(LiquidityHandoffError):
        validate_schema_observation_file(
            path.resolve(),
            expected_sha256=_sha256(path),
            repository_root=ROOT,
        )


def test_goal_preflight_is_zero_artifact_and_deterministic() -> None:
    assert run_goal(ROOT)
    first = (ROOT / MANIFEST).read_bytes()
    assert run_goal(ROOT)
    assert (ROOT / MANIFEST).read_bytes() == first
    assert audit_goal(ROOT)


def test_handoff_module_has_no_network_or_provider_client_imports() -> None:
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imports.isdisjoint(
        {"tushare", "baostock", "requests", "httpx", "urllib", "socket", "keyring"}
    )
