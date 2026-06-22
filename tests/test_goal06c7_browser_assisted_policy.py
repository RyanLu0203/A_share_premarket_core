from __future__ import annotations

import ast
import shutil
from pathlib import Path

from ashare_premarket.providers.browser_provider_policy import browser_assisted_enabled
from ashare_premarket.providers.browser_provider_switches import browser_provider_project_default

ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "configs", root / "configs")
    return root


def test_browser_assisted_provider_is_disabled_by_default(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    monkeypatch.delenv("ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER", raising=False)
    assert browser_provider_project_default(root) is False
    assert browser_assisted_enabled(root, cli_enabled=False) is False
    assert browser_assisted_enabled(root, cli_enabled=True) is False


def test_browser_assisted_provider_requires_cli_and_env(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    monkeypatch.setenv("ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER", "1")
    assert browser_assisted_enabled(root, cli_enabled=False) is False
    assert browser_assisted_enabled(root, cli_enabled=True) is True


def test_browser_runtime_is_dynamic_import_only() -> None:
    path = ROOT / "src/ashare_premarket/providers/browser_assisted_provider.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert "cloakbrowser" not in imports
    assert "playwright" not in imports


def test_browser_assisted_policy_forbids_raw_artifacts() -> None:
    text = (ROOT / "configs/providers/browser_assisted_provider_config.yaml").read_text(encoding="utf-8")
    for forbidden in ["raw_html_commit", "raw_payload_commit", "cookie_commit", "browser_profile_commit"]:
        assert forbidden in text
