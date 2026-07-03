from __future__ import annotations

import re
from pathlib import Path

from ashare_premarket.validation.workflow_status import _unexpected_goal10b_backtest_outputs


ROOT = Path(__file__).resolve().parents[1]

UNSAFE_RELATIVE_TO_PATTERN = re.compile(r"str\(\s*[\w.\[\]]+\.relative_to\(")


def test_relative_to_as_posix_returns_forward_slashes() -> None:
    nested = ROOT / "outputs" / "backtest"
    assert nested.relative_to(ROOT).as_posix() == "outputs/backtest"
    assert "\\" not in nested.relative_to(ROOT).as_posix()


def test_relative_to_as_posix_matches_forward_slash_allowlist_entries() -> None:
    sample = ROOT / "outputs/backtest/goal10b_recommendation_group_metrics.csv"
    assert sample.relative_to(ROOT).as_posix() == "outputs/backtest/goal10b_recommendation_group_metrics.csv"


def test_committed_backtest_outputs_are_recognized_by_workflow_audit() -> None:
    assert _unexpected_goal10b_backtest_outputs(ROOT) == []


def test_no_unsafe_str_relative_to_pattern_under_src() -> None:
    offenders: list[str] = []
    for path in sorted((ROOT / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if UNSAFE_RELATIVE_TO_PATTERN.search(line):
                offenders.append(f"{path.relative_to(ROOT).as_posix()}:{lineno}")
    assert offenders == []
