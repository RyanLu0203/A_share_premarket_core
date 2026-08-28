from __future__ import annotations

from pathlib import Path

from ashare_premarket.validation.public_release import _CONTENT_PATTERNS


def test_owner_specific_home_paths_are_detected() -> None:
    payload = b"/" + b"Users" + b"/alice/private/project"
    assert _CONTENT_PATTERNS["absolute_user_home"].search(payload)


def test_public_placeholders_do_not_identify_a_user() -> None:
    payload = b"<private-macos-home>/Desktop/project"
    assert not _CONTENT_PATTERNS["absolute_user_home"].search(payload)


def test_secret_patterns_are_high_signal() -> None:
    fake_key = b"AK" + b"IA" + b"A" * 16
    assert _CONTENT_PATTERNS["aws_access_key"].search(fake_key)
    assert not _CONTENT_PATTERNS["aws_access_key"].search(b"AKShare provider")
