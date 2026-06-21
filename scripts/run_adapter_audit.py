from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.ops.adapter_audit import run_adapter_audit


if __name__ == "__main__":
    raise SystemExit(0 if run_adapter_audit(ROOT) else 1)
