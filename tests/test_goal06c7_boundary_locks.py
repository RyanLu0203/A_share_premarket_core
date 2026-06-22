from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06c7_does_not_import_locked_downstream_modules() -> None:
    locked_fragments = {
        "risk_overlay",
        "position_band",
        "recommendation",
        "dashboard",
        "paper_trading",
        "broker",
        "live_trading",
        "production_model",
        "dqn",
        "reinforcement_learning",
    }
    failures: list[str] = []
    for path in (ROOT / "src/ashare_premarket/providers").glob("*.py"):
        if "provider_ladder" not in path.name and "browser_" not in path.name and "local_import" not in path.name:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.lower() for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").lower()]
            for name in names:
                if any(fragment in name for fragment in locked_fragments):
                    failures.append(f"{path.name} imports {name}")
    assert failures == []


def test_cloakbrowser_reference_can_be_named_without_static_import() -> None:
    path = ROOT / "src/ashare_premarket/providers/browser_assisted_provider.py"
    text = path.read_text(encoding="utf-8")
    assert "importlib.import_module(\"cloakbrowser\")" in text
    tree = ast.parse(text)
    assert all(not (isinstance(node, ast.Import) and any(alias.name == "cloakbrowser" for alias in node.names)) for node in ast.walk(tree))
