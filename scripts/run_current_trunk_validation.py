from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.gates import run_current_trunk_validation


if __name__ == "__main__":
    raise SystemExit(0 if run_current_trunk_validation(ROOT) else 1)
