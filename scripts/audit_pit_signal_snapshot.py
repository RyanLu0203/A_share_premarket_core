from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.features.pit_signal_store import audit_pit_signal_snapshot


if __name__ == "__main__":
    raise SystemExit(0 if audit_pit_signal_snapshot(ROOT) else 1)
