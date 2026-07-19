from __future__ import annotations

from pathlib import Path

import pytest

from ashare_premarket.alpha_validation.store import write_local_validation_run
from ashare_premarket.quant_foundation.contracts import canonical_checksum


def _result() -> dict[str, object]:
    feature = {"date": "2026-01-01", "symbol": "600036.SH", "x": 1.0}
    feature["checksum"] = canonical_checksum(feature)
    label = {
        "date": "2026-01-01",
        "symbol": "600036.SH",
        "horizon_trading_days": 1,
        "forward_return": 0.01,
        "label_status": "AVAILABLE",
    }
    label["checksum"] = canonical_checksum(label)
    result: dict[str, object] = {
        "goal_id": "GOAL-12",
        "code_commit": "a" * 40,
        "status": "COMPLETE_RESEARCH_ONLY",
        "research_only": True,
        "production_ready": False,
        "ready_factor_count": 0,
        "production_model_promoted": False,
        "data_audit": {"status": "PASS"},
        "feature_rows": [feature],
        "label_rows": [label],
        "splits": {"random_date_split_used": False},
        "single_factor_results": [],
        "null_controls": [],
        "fdr_results": {},
        "combined_models": [],
        "robustness": {},
        "decisions": [],
    }
    result["checksum"] = canonical_checksum(result)
    return result


def test_local_store_is_immutable_checksumed_and_byte_reproducible(tmp_path: Path) -> None:
    manifests = []
    byte_sets = []
    for name in ("repo-a", "repo-b"):
        repository = tmp_path / name
        output = repository / "outputs/local/goal12"
        manifest = write_local_validation_run(repository, output, "run-001", _result())
        run = output / "run-001"
        manifests.append(manifest)
        byte_sets.append({path.name: path.read_bytes() for path in run.iterdir()})
        assert (run / "features.csv").is_file()
        assert (run / "labels.csv").is_file()
        assert (run / "null_controls.json").is_file()
        assert manifest["artifact_policy"] == "LOCAL_IGNORED_RESEARCH_ONLY"
        assert manifest["code_commit"] == "a" * 40
        assert manifest["production_ready"] is False
        assert manifest["ready_factor_count"] == 0
    assert manifests[0] == manifests[1]
    assert byte_sets[0] == byte_sets[1]


def test_local_store_rejects_unsafe_mutable_or_unlocked_results(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    with pytest.raises(ValueError, match="goal12_output_must_be_under_outputs_local"):
        write_local_validation_run(repository, tmp_path / "outside", "run", _result())
    with pytest.raises(ValueError, match="invalid_goal12_run_id"):
        write_local_validation_run(
            repository, repository / "outputs/local", "../escape", _result()
        )
    write_local_validation_run(
        repository, repository / "outputs/local", "run", _result()
    )
    with pytest.raises(ValueError, match="goal12_run_directory_already_exists"):
        write_local_validation_run(
            repository, repository / "outputs/local", "run", _result()
        )
    unlocked = _result()
    unlocked["production_ready"] = True
    unlocked["checksum"] = canonical_checksum(
        {key: value for key, value in unlocked.items() if key != "checksum"}
    )
    with pytest.raises(ValueError, match="goal12_result_production_lock_violation"):
        write_local_validation_run(
            repository, repository / "outputs/local", "unlocked", unlocked
        )
