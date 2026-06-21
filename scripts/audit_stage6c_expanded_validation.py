from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.stage6c import audit_stage6c_expanded_validation


if __name__ == "__main__":
    raise SystemExit(0 if audit_stage6c_expanded_validation(ROOT) else 1)
