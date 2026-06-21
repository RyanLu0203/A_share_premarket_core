from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.gates import run_e2e_verification


if __name__ == "__main__":
    raise SystemExit(0 if run_e2e_verification(ROOT) else 1)
