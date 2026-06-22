from __future__ import annotations

from ashare_premarket.providers.failure_classification import classify_provider_failure


def test_http_403_maps_to_access_failure() -> None:
    result = classify_provider_failure(status_code=403)
    assert result.failure_class == "HTTP_403_FORBIDDEN"
    assert result.failure_layer == "http_access"
    assert result.fallback_allowed is True


def test_http_429_maps_to_rate_limit() -> None:
    result = classify_provider_failure(status_code=429)
    assert result.failure_class == "HTTP_429_RATE_LIMITED"
    assert result.retry_allowed is True


def test_http_5xx_maps_to_provider_error() -> None:
    result = classify_provider_failure(status_code=503)
    assert result.failure_class == "HTTP_5XX_PROVIDER_ERROR"
    assert result.requires_provider_replacement is True


def test_terms_or_robots_maps_to_http_access_layer() -> None:
    result = classify_provider_failure(response_text="access denied by robots policy")
    assert result.failure_class == "TERMS_OR_ROBOTS_RESTRICTED"
    assert result.failure_layer == "http_access"
