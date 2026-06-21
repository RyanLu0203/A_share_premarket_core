from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.workflow_status import run_workflow_status_audit


if __name__ == "__main__":
    raise SystemExit(0 if run_workflow_status_audit(ROOT) else 1)
