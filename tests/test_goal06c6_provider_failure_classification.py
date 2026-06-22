from __future__ import annotations

from pathlib import Path

from ashare_premarket.providers.failure_classification import (
    FAILURE_CLASSES,
    audit_provider_failure_classification,
    classify_provider_failure,
    classify_provider_success,
)

ROOT = Path(__file__).resolve().parents[1]


def test_required_failure_classes_exist() -> None:
    required = {
        "PROVIDER_OK",
        "NETWORK_DISABLED_BY_POLICY",
        "HTTP_403_FORBIDDEN",
        "HTTP_429_RATE_LIMITED",
        "BOT_CHALLENGE_DETECTED",
        "CAPTCHA_OR_VERIFY_PAGE",
        "HTML_RETURNED_INSTEAD_OF_DATA",
        "DEPENDENCY_MISSING",
    }
    assert required <= set(FAILURE_CLASSES)


def test_bot_and_captcha_are_classified_not_bypassed() -> None:
    captcha = classify_provider_failure(response_text="<html>captcha verify</html>")
    assert captcha.failure_class == "CAPTCHA_OR_VERIFY_PAGE"
    assert captcha.retry_allowed is False

    challenge = classify_provider_failure(response_text="robot safety check")
    assert challenge.failure_class == "BOT_CHALLENGE_DETECTED"
    assert challenge.retry_allowed is False


def test_http_403_429_and_success_classification() -> None:
    assert classify_provider_failure(status_code=403).failure_class == "HTTP_403_FORBIDDEN"
    assert classify_provider_failure(status_code=429).failure_class == "HTTP_429_RATE_LIMITED"
    ok = classify_provider_success(rows_returned=1, schema_valid=True)
    assert ok.failure_class == "PROVIDER_OK"
    assert ok.retry_allowed is False


def test_provider_failure_classification_audit_writes_report() -> None:
    assert audit_provider_failure_classification(ROOT)
    report = ROOT / "outputs/audits/provider_failure_classification_audit.md"
    assert "Status: `PASS`" in report.read_text(encoding="utf-8")
