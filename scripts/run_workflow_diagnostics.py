from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics


if __name__ == "__main__":
    raise SystemExit(0 if run_workflow_diagnostics(ROOT) else 1)
