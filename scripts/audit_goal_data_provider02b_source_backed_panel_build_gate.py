from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.providers.goal_data_provider02b import audit_goal_data_provider02b_source_backed_panel_build_gate


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal_data_provider02b_source_backed_panel_build_gate(Path(__file__).resolve().parents[1]) else 1)
