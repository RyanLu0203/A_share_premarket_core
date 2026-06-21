from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.ops.safety import run_safety_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_safety_gate(ROOT) else 1)
