from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.workflow_cleanliness import audit_workflow_cleanliness


if __name__ == "__main__":
    raise SystemExit(0 if audit_workflow_cleanliness(ROOT) else 1)
