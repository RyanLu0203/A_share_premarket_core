from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.labels.label_builder import audit_label_snapshot


if __name__ == "__main__":
    raise SystemExit(0 if audit_label_snapshot(ROOT) else 1)
