from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.architecture.goal_architecture_refactor03 import run_goal_architecture_refactor03_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_architecture_refactor03_gate(Path(__file__).resolve().parents[1]) else 1)
