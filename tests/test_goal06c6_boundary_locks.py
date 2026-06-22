from __future__ import annotations

import ast
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06c6_workflow_row_blocks_goal06d_until_engineering_pilot() -> None:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    assert rows["goal06c6_source_backed_engineering_pilot_bundle"]["status"] == "implemented_review_only"
    assert rows["goal06c6_source_backed_engineering_pilot_bundle"]["allowed_next_action"] == "block_goal06d_until_engineering_pilot"
    assert rows["goal06d_model_comparison_calibration"]["status"] == "future_review_only"
    assert "goal06c6" in rows["goal06d_model_comparison_calibration"]["allowed_next_action"]


def test_no_cloakbrowser_or_bypass_dependency_is_added() -> None:
    dependency_files = ["pyproject.toml", "requirements.txt", "setup.cfg", "setup.py"]
    dependency_text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in dependency_files if (ROOT / path).exists()).lower()
    for forbidden in ["cloakbrowser", "cloakbrowser", "selenium-stealth", "undetected-chromedriver", "proxy-rotation", "captcha-solver"]:
        assert forbidden not in dependency_text


def test_no_active_bypass_module_imports() -> None:
    forbidden_import_fragments = {"cloakbrowser", "selenium_stealth", "undetected_chromedriver", "captcha_solver", "proxy_rotation"}
    failures: list[str] = []
    for base in [ROOT / "src", ROOT / "scripts"]:
        for path in base.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name.lower() for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [(node.module or "").lower()]
                for name in names:
                    if any(fragment in name for fragment in forbidden_import_fragments):
                        failures.append(f"{path.relative_to(ROOT)} imports {name}")
    assert failures == []
