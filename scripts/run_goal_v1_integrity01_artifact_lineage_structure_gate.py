from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.goal_v1_integrity01 import run_goal_v1_integrity01_artifact_lineage_structure_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT) else 1)
