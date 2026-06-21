from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.gates import audit_existing_modules


if __name__ == "__main__":
    raise SystemExit(0 if audit_existing_modules(ROOT) else 1)
