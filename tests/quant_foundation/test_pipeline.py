from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from ashare_premarket.quant_foundation.contracts import FORBIDDEN_ACTION_FIELDS, canonical_checksum
from ashare_premarket.quant_foundation.features import load_feature_config
from ashare_premarket.quant_foundation.pipeline import run_quant_intelligence_pipeline
from ashare_premarket.quant_foundation.store import write_local_research_run
from .conftest import make_snapshot

ROOT = Path(__file__).resolve().parents[2]


def _labels(snapshot_id: str, feature_dates: list[tuple[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, (trade_date, symbol) in enumerate(feature_dates):
        label: dict[str, object] = {
            "date": trade_date,
            "symbol": symbol,
            "label_available_at": (
                date.fromisoformat(trade_date) + timedelta(days=1)
            ).isoformat(),
            "forward_return": (index % 11 - 5) / 1000.0,
            "label_version": "synthetic_forward_1d_v1",
            "source_snapshot_id": snapshot_id,
        }
        label["checksum"] = canonical_checksum(label)
        rows.append(label)
    return rows


def _pipeline() -> dict[str, object]:
    snapshot = make_snapshot()
    labels = _labels(snapshot.snapshot_id, [(row.date, row.symbol) for row in snapshot.rows])
    return run_quant_intelligence_pipeline(snapshot, labels, load_feature_config(ROOT))


def test_pipeline_is_integrated_reproducible_and_keeps_labels_separate() -> None:
    first = _pipeline()
    second = _pipeline()

    assert first == second
    assert first["status"] == "COMPLETE_RESEARCH_ONLY"
    assert first["research_only"] is True
    assert first["feature_rows"]
    assert first["alpha_rows"]
    assert first["linear_ranker"]["scores"]
    assert first["evaluation"]["policy_metrics"]
    assert "labels" not in first
    assert first["ready_factor_count"] == 0
    assert first["production_model_promoted"] is False
    assert first["checksum"] == canonical_checksum(
        {key: value for key, value in first.items() if key != "checksum"}
    )


def test_local_store_is_immutable_and_byte_reproducible(tmp_path: Path) -> None:
    result = _pipeline()
    manifests = []
    file_sets = []
    for name in ("repo-a", "repo-b"):
        repository = tmp_path / name
        local_root = repository / "outputs" / "local" / "goal11"
        manifest = write_local_research_run(
            repository,
            local_root,
            "run-001",
            result,
        )
        run_directory = local_root / "run-001"
        manifests.append(manifest)
        file_sets.append(
            {
                path.name: path.read_bytes()
                for path in run_directory.iterdir()
                if path.is_file()
            }
        )
        assert (run_directory / "features.csv").exists()
        assert (run_directory / "alpha_scores.csv").exists()
        assert (run_directory / "linear_scores.csv").exists()
        assert (run_directory / "linear_ranker.json").exists()
        assert (run_directory / "evaluation.json").exists()
        assert (run_directory / "run_manifest.json").exists()
    assert manifests[0] == manifests[1]
    assert file_sets[0] == file_sets[1]
    assert manifests[0]["artifact_policy"] == "LOCAL_IGNORED_RESEARCH_ONLY"
    assert "labels.csv" not in file_sets[0]


def test_local_store_rejects_unsafe_or_mutable_targets(tmp_path: Path) -> None:
    result = _pipeline()
    repository = tmp_path / "repo"
    with pytest.raises(ValueError, match="goal11_output_must_be_under_outputs_local"):
        write_local_research_run(repository, tmp_path / "outside", "run-001", result)
    with pytest.raises(ValueError, match="invalid_goal11_run_id"):
        write_local_research_run(
            repository,
            repository / "outputs" / "local",
            "../escape",
            result,
        )
    local_root = repository / "outputs" / "local"
    write_local_research_run(repository, local_root, "run-001", result)
    with pytest.raises(ValueError, match="goal11_run_directory_already_exists"):
        write_local_research_run(repository, local_root, "run-001", result)


def test_integrated_output_contains_no_actionable_schema() -> None:
    result = _pipeline()

    def keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(map(str, value)) | set().union(*(keys(item) for item in value.values()))
        if isinstance(value, (list, tuple)):
            return set().union(*(keys(item) for item in value)) if value else set()
        return set()

    assert not (FORBIDDEN_ACTION_FIELDS & {key.lower() for key in keys(result)})
