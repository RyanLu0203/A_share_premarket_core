from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.providers.failure_classification import audit_provider_failure_classification


if __name__ == "__main__":
    raise SystemExit(0 if audit_provider_failure_classification(ROOT) else 1)
