from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.data.coverage import audit_data_source_coverage


if __name__ == "__main__":
    raise SystemExit(0 if audit_data_source_coverage(ROOT) else 1)
