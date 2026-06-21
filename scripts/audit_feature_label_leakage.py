from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.datasets.feature_label_merge import audit_feature_label_leakage


if __name__ == "__main__":
    raise SystemExit(0 if audit_feature_label_leakage(ROOT) else 1)
