from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.gates import run_program_validation_profile


if __name__ == "__main__":
    raise SystemExit(0 if run_program_validation_profile(ROOT) else 1)
