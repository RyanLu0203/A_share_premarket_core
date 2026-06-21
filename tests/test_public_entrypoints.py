from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import PUBLIC_COMMANDS


ROOT = Path(__file__).resolve().parents[1]


def test_public_entrypoints_exist() -> None:
    missing = [path for path in PUBLIC_COMMANDS if not (ROOT / path).exists()]
    assert missing == []


def test_public_entrypoints_are_clean_wrappers() -> None:
    for path in PUBLIC_COMMANDS:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "fintechgp" not in text
        assert "legacy_impl" not in text
