from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.governance.goal_global_codebase_consolidation_stock_chart01 import (
    audit_goal_global_codebase_consolidation_stock_chart01,
)


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal_global_codebase_consolidation_stock_chart01(Path(__file__).resolve().parents[1]) else 1)
