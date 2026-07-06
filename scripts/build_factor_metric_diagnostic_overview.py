from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.research.factor_diagnostic_overview import build_factor_diagnostic_overview


if __name__ == "__main__":
    path = build_factor_diagnostic_overview(ROOT)
    print(f"Wrote research-only diagnostic overview: {path}")
