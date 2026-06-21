from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.training.supervised_baseline import audit_supervised_baseline_training


if __name__ == "__main__":
    raise SystemExit(0 if audit_supervised_baseline_training(ROOT) else 1)
