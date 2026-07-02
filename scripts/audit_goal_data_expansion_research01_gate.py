from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.data_expansion.goal_data_expansion_research01 import audit_goal_data_expansion_research01_gate


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal_data_expansion_research01_gate(Path(__file__).resolve().parents[1]) else 1)

