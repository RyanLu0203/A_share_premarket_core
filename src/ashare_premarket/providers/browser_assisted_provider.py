from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from typing import Iterable


@dataclass
class BrowserFetchResult:
    key: str
    url: str
    status: str
    http_status: str = ""
    content_type: str = ""
    body_text: str = ""
    failure_class: str = ""
    failure_layer: str = ""
    safe_notes: str = ""


def browser_dependency_status() -> str:
    if _module_available("cloakbrowser") and _module_available("playwright.sync_api"):
        return "AVAILABLE"
    return "BROWSER_RUNTIME_DEPENDENCY_MISSING"


def fetch_urls_with_browser(urls: Iterable[tuple[str, str]], timeout_ms: int = 15000) -> list[BrowserFetchResult]:
    if browser_dependency_status() != "AVAILABLE":
        return [
            BrowserFetchResult(
                key=key,
                url=url,
                status="FAIL",
                failure_class="BROWSER_RUNTIME_DEPENDENCY_MISSING",
                failure_layer="dependency",
                safe_notes="browser runtime dependency missing",
            )
            for key, url in urls
        ]
    module = importlib.import_module("cloakbrowser")
    launch = getattr(module, "launch")
    browser = None
    results: list[BrowserFetchResult] = []
    try:
        browser = launch(headless=True, humanize=False, geoip=False)
        for key, url in urls:
            page = None
            try:
                page = browser.new_page()
                response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                status = getattr(response, "status", "") if response is not None else ""
                headers = getattr(response, "headers", {}) if response is not None else {}
                content_type = headers.get("content-type", "") if isinstance(headers, dict) else ""
                body_text = _body_text(page)
                if int(status or 0) == 200 and body_text:
                    results.append(BrowserFetchResult(key=key, url=url, status="PASS", http_status=str(status), content_type=content_type, body_text=body_text, safe_notes="HTTP 200; body parsed in memory only"))
                else:
                    results.append(BrowserFetchResult(key=key, url=url, status="FAIL", http_status=str(status), content_type=content_type, failure_class="BROWSER_NAVIGATION_FAILED", failure_layer="browser_runtime", safe_notes=f"HTTP {status}; no structured body"))
            except Exception as exc:
                failure_class, failure_layer = _class_for_exception(exc)
                results.append(BrowserFetchResult(key=key, url=url, status="FAIL", failure_class=failure_class, failure_layer=failure_layer, safe_notes=f"{type(exc).__name__}: {_safe_note(exc)}"))
            finally:
                if page is not None:
                    try:
                        page.close()
                    except Exception:
                        pass
    except Exception as exc:
        failure_class, failure_layer = _class_for_exception(exc)
        results = [
            BrowserFetchResult(
                key=key,
                url=url,
                status="FAIL",
                failure_class=failure_class,
                failure_layer=failure_layer,
                safe_notes=f"browser launch failed: {type(exc).__name__}: {_safe_note(exc)}",
            )
            for key, url in urls
        ]
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass
    return results


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def _body_text(page: object) -> str:
    method = getattr(page, "text_content", None)
    if callable(method):
        try:
            text = method("body", timeout=1000)
            return str(text or "")
        except Exception:
            return ""
    return ""


def _class_for_exception(exc: BaseException) -> tuple[str, str]:
    message = str(exc).lower()
    if "err_empty_response" in message:
        return "BROWSER_NET_EMPTY_RESPONSE", "network_transport"
    if "timeout" in message:
        return "BROWSER_NAVIGATION_FAILED", "browser_runtime"
    if "name_not_resolved" in message:
        return "DNS_RESOLUTION_FAILURE", "network_transport"
    if "ssl" in message or "certificate" in message:
        return "TLS_SSL_FAILURE", "network_transport"
    return "BROWSER_RUNTIME_LAUNCH_FAILED" if "launch" in message else "BROWSER_NAVIGATION_FAILED", "browser_runtime"


def _safe_note(value: object) -> str:
    return str(value).replace("\n", " ").replace("\r", " ")[:240]
