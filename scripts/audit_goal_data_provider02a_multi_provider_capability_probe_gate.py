from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.providers.goal_data_provider02a import audit_goal_data_provider02a_multi_provider_capability_probe_gate


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal_data_provider02a_multi_provider_capability_probe_gate(Path(__file__).resolve().parents[1]) else 1)
