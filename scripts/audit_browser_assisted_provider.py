from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.providers.browser_provider_events import audit_browser_assisted_provider


if __name__ == "__main__":
    raise SystemExit(0 if audit_browser_assisted_provider(ROOT) else 1)
