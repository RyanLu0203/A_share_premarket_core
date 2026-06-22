from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.providers.failure_classification import FAILURE_CLASSES, classification_for_class

ROOT = Path(__file__).resolve().parents[1]


def test_local_storage_failures_are_storage_bundle_layer() -> None:
    missing = classification_for_class("LOCAL_DATA_ROOT_MISSING")
    not_writable = classification_for_class("LOCAL_DATA_ROOT_NOT_WRITABLE")
    assert missing.failure_layer == "storage_bundle"
    assert not_writable.failure_layer == "storage_bundle"


def test_heavy_parquet_or_db_staged_maps_to_git_policy_failure() -> None:
    result = classification_for_class("HEAVY_DATA_STAGED_FOR_GIT")
    assert result.failure_layer == "storage_bundle"
    assert result.requires_user_action is True


def test_workflow_status_and_goal06d_unlock_are_governance_failures() -> None:
    status = classification_for_class("WORKFLOW_STATUS_INCONSISTENT")
    goal06d = classification_for_class("GOAL06D_UNBLOCKED_WITHOUT_ENGINEERING_PILOT")
    assert status.failure_layer == "workflow_governance"
    assert goal06d.failure_layer == "workflow_governance"
    assert goal06d.goal06d_allowed_after_failure is False


def test_active_taxonomy_does_not_keep_legacy_generic_classes() -> None:
    assert "NETWORK_ERROR" not in FAILURE_CLASSES
    assert "TIMEOUT" not in FAILURE_CLASSES
    assert "SCHEMA_CHANGED" not in FAILURE_CLASSES
    config = json.loads((ROOT / "configs/providers/provider_failure_classification.yaml").read_text(encoding="utf-8"))
    configured = [failure for failures in config["failure_classes"].values() for failure in failures]
    assert "NETWORK_ERROR" not in configured
    assert "TIMEOUT" not in configured
    assert "SCHEMA_CHANGED" not in configured
