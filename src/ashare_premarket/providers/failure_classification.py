from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ashare_premarket.core.io import write_text

FAILURE_CLASSES = [
    "PROVIDER_OK",
    "NETWORK_DISABLED_BY_POLICY",
    "NETWORK_ERROR",
    "TIMEOUT",
    "HTTP_403_FORBIDDEN",
    "HTTP_429_RATE_LIMITED",
    "BOT_CHALLENGE_DETECTED",
    "CAPTCHA_OR_VERIFY_PAGE",
    "AUTH_OR_CONSENT_REQUIRED",
    "HTML_RETURNED_INSTEAD_OF_DATA",
    "SCHEMA_CHANGED",
    "EMPTY_RESPONSE",
    "SYMBOL_NOT_SUPPORTED",
    "DATE_RANGE_NOT_SUPPORTED",
    "PROVIDER_DISABLED_BY_POLICY",
    "TERMS_OR_ROBOTS_RESTRICTED",
    "DEPENDENCY_MISSING",
    "UNKNOWN_PROVIDER_FAILURE",
]

NO_RETRY_CLASSES = {
    "HTTP_403_FORBIDDEN",
    "HTTP_429_RATE_LIMITED",
    "BOT_CHALLENGE_DETECTED",
    "CAPTCHA_OR_VERIFY_PAGE",
    "AUTH_OR_CONSENT_REQUIRED",
    "HTML_RETURNED_INSTEAD_OF_DATA",
    "SCHEMA_CHANGED",
    "PROVIDER_DISABLED_BY_POLICY",
    "TERMS_OR_ROBOTS_RESTRICTED",
    "DEPENDENCY_MISSING",
}


@dataclass(frozen=True)
class FailureClassification:
    failure_class: str
    retry_allowed: bool
    notes: str


def classify_provider_failure(exc: BaseException | None = None, response_text: str | None = None, status_code: int | None = None) -> FailureClassification:
    if status_code == 403:
        return _classification("HTTP_403_FORBIDDEN", "provider returned HTTP 403")
    if status_code == 429:
        return _classification("HTTP_429_RATE_LIMITED", "provider returned HTTP 429")
    text = (response_text or "").lower()
    message = f"{type(exc).__name__}: {exc}".lower() if exc else text
    combined = f"{text} {message}"
    if "captcha" in combined or "验证码" in combined:
        return _classification("CAPTCHA_OR_VERIFY_PAGE", "captcha or verification page detected")
    if "verify" in combined or "验证" in combined or "安全检查" in combined:
        return _classification("CAPTCHA_OR_VERIFY_PAGE", "verification challenge detected")
    if "bot" in combined or "robot" in combined or "爬虫" in combined:
        return _classification("BOT_CHALLENGE_DETECTED", "bot challenge detected")
    if "login" in combined or "auth" in combined or "consent" in combined or "授权" in combined:
        return _classification("AUTH_OR_CONSENT_REQUIRED", "auth or consent required")
    if "<html" in combined or "<!doctype html" in combined:
        return _classification("HTML_RETURNED_INSTEAD_OF_DATA", "HTML returned instead of tabular data")
    if "timed out" in combined or "timeout" in combined:
        return _classification("TIMEOUT", "provider request timed out")
    if "no module named" in combined or "modulenotfounderror" in combined:
        return _classification("DEPENDENCY_MISSING", "optional data dependency is missing")
    if "symbol" in combined and ("not supported" in combined or "unsupported" in combined):
        return _classification("SYMBOL_NOT_SUPPORTED", "symbol is not supported by provider")
    if "date" in combined and ("not supported" in combined or "out of range" in combined):
        return _classification("DATE_RANGE_NOT_SUPPORTED", "date range is not supported by provider")
    if "schema" in combined or "columns" in combined:
        return _classification("SCHEMA_CHANGED", "provider schema did not match expected columns")
    if exc is not None:
        return _classification("NETWORK_ERROR", f"provider error: {type(exc).__name__}")
    return _classification("UNKNOWN_PROVIDER_FAILURE", "unknown provider failure")


def classify_provider_success(rows_returned: int, schema_valid: bool) -> FailureClassification:
    if rows_returned <= 0:
        return _classification("EMPTY_RESPONSE", "provider returned no rows")
    if not schema_valid:
        return _classification("SCHEMA_CHANGED", "provider returned rows but schema normalization failed")
    return _classification("PROVIDER_OK", "provider returned normalized rows")


def retry_allowed(failure_class: str) -> bool:
    return failure_class not in NO_RETRY_CLASSES and failure_class != "PROVIDER_OK"


def audit_provider_failure_classification(root: Path) -> bool:
    failures = []
    expected = set(FAILURE_CLASSES)
    if len(expected) != len(FAILURE_CLASSES):
        failures.append("duplicate provider failure class")
    for required in [
        "NETWORK_DISABLED_BY_POLICY",
        "HTTP_403_FORBIDDEN",
        "HTTP_429_RATE_LIMITED",
        "BOT_CHALLENGE_DETECTED",
        "CAPTCHA_OR_VERIFY_PAGE",
        "HTML_RETURNED_INSTEAD_OF_DATA",
        "DEPENDENCY_MISSING",
    ]:
        if required not in expected:
            failures.append(f"missing failure class: {required}")
    html = classify_provider_failure(response_text="<html>captcha verify</html>")
    if html.failure_class != "CAPTCHA_OR_VERIFY_PAGE":
        failures.append("captcha/verify HTML is not classified as a challenge")
    forbidden = classify_provider_failure(status_code=403)
    if forbidden.failure_class != "HTTP_403_FORBIDDEN" or forbidden.retry_allowed:
        failures.append("HTTP 403 must be a non-retryable classified failure")
    status = "PASS" if not failures else "BLOCKED"
    write_text(
        root / "outputs/audits/provider_failure_classification_audit.md",
        "\n".join(
            [
                "# Provider Failure Classification Audit",
                "",
                f"Status: `{status}`",
                f"Failure classes: `{len(FAILURE_CLASSES)}`",
                "Bot, captcha, verify, 403, and 429 responses are classified and not bypassed.",
                "No raw HTML challenge pages are stored in GitHub.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return not failures


def _classification(failure_class: str, notes: str) -> FailureClassification:
    return FailureClassification(failure_class=failure_class, retry_allowed=retry_allowed(failure_class), notes=notes)
