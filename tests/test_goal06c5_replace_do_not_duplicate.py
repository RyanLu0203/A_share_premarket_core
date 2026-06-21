from __future__ import annotations

from pathlib import Path

from ashare_premarket.validation.engineering_panel import rebuild_stage6c_from_engineering_panel

ROOT = Path(__file__).resolve().parents[1]


def test_contract_demo_does_not_replace_active_stage6c_path() -> None:
    assert rebuild_stage6c_from_engineering_panel(ROOT)
    audit = (ROOT / "outputs/audits/active_path_replacement_audit.md").read_text(encoding="utf-8")
    assert "not_replaced_contract_demo_only" in audit
    assert "kept_as_fixture" in audit
    assert "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv" in audit
    assert (ROOT / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv").exists()


def test_replace_policy_doc_exists() -> None:
    policy = ROOT / "docs/architecture/REPLACE_DO_NOT_DUPLICATE_POLICY.md"
    assert policy.exists()
    text = policy.read_text(encoding="utf-8")
    assert "engineering_pilot" in text
