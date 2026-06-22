from __future__ import annotations

from ashare_premarket.providers.failure_classification import classify_provider_failure
from ashare_premarket.providers.failure_events import build_failure_events
from ashare_premarket.providers.provider_attempt_log import make_attempt


def test_html_challenge_page_maps_to_antibot_or_html_class() -> None:
    result = classify_provider_failure(response_text="<html><title>security check</title>robot challenge</html>")
    assert result.failure_class == "BOT_CHALLENGE_DETECTED"
    assert result.failure_layer == "anti_bot_access"


def test_captcha_verify_page_maps_to_captcha_class() -> None:
    result = classify_provider_failure(response_text="<html>captcha verify page</html>")
    assert result.failure_class == "CAPTCHA_OR_VERIFY_PAGE"
    assert result.retry_allowed is False


def test_javascript_and_login_walls_are_specific() -> None:
    assert classify_provider_failure(response_text="please enable javascript").failure_class == "JS_CHALLENGE_DETECTED"
    assert classify_provider_failure(response_text="login or consent wall").failure_class == "LOGIN_OR_CONSENT_WALL_DETECTED"


def test_event_notes_suppress_raw_html() -> None:
    attempt = make_attempt(
        "akshare",
        "stock_zh_a_spot_em",
        network_enabled=True,
        status="FAIL",
        failure_class="HTML_RETURNED_INSTEAD_OF_DATA",
        notes="<html>captcha body should not be stored</html>",
    )
    event = build_failure_events([attempt], network_enabled=True)[0]
    assert event["safe_notes"] == "html/challenge content suppressed"
