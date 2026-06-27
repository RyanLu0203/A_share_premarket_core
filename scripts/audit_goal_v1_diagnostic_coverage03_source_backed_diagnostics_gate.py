from __future__ import annotations

import sys
from _bootstrap import ROOT
from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
    audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate,
)


if __name__ == "__main__":
    sys.exit(0 if audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(ROOT) else 1)
