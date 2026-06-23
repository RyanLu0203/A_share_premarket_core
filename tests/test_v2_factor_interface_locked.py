from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v2_factor_research_contract_is_locked_and_disabled() -> None:
    text = (ROOT / "configs/factors/v2_factor_research_contract.yaml").read_text(encoding="utf-8")
    assert "status: planned_locked" in text
    assert "enabled: false" in text
    assert "active_in_v1: false" in text
    assert "factor_mining" in text
    assert "RankIC_mining" in text


def test_v2_factor_research_has_no_active_runner_or_outputs() -> None:
    forbidden_paths = [
        ROOT / "scripts/run_factor_research.py",
        ROOT / "src/ashare_premarket/factors/factor_mining.py",
        ROOT / "src/ashare_premarket/factors/ic_analysis.py",
        ROOT / "outputs/factors",
    ]
    assert all(not path.exists() for path in forbidden_paths)
    active_scripts = "\n".join(path.name for path in (ROOT / "scripts").glob("*.py"))
    assert "run_factor_research.py" not in active_scripts
    assert "ic_mining" not in active_scripts.lower()
    assert "rankic" not in active_scripts.lower()


def test_v2_factor_docs_mark_placeholder_inactive() -> None:
    text = (ROOT / "docs/factors/V2_FACTOR_RESEARCH_INTERFACE.md").read_text(encoding="utf-8")
    assert "Status: `planned_locked`" in text
    assert "disabled in V1" in text
    assert "No V2 factor mining runner" in text
