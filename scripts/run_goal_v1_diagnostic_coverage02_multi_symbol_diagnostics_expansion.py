from __future__ import annotations

import sys
from _bootstrap import ROOT
from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import (
    run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion,
)


if __name__ == "__main__":
    sys.exit(0 if run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(ROOT) else 1)
