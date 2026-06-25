from _bootstrap import ROOT

from ashare_premarket.review_diagnostics.goal09 import audit_goal09_position_band_diagnostics_prototype


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal09_position_band_diagnostics_prototype(ROOT) else 1)
