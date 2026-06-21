from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_locked_capabilities_remain_false() -> None:
    locked = json.loads((ROOT / "configs/project/locked_capabilities.json").read_text(encoding="utf-8"))
    for key in [
        "position_band_recommendation",
        "signal_backtest",
        "portfolio_backtest",
        "dashboard",
        "paper_trading",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "dqn_rl",
    ]:
        assert locked[key] is False


def test_active_source_has_no_locked_imports() -> None:
    import ast

    for path in (ROOT / "src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.lower() for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").lower()]
            assert not any(token in name for name in names for token in ["dashboard", "dqn", "paper_trading"])
