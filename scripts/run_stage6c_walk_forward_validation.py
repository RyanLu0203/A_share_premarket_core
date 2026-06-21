from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.stage6c import run_stage6c_walk_forward_validation


if __name__ == "__main__":
    run_stage6c_walk_forward_validation(ROOT)
