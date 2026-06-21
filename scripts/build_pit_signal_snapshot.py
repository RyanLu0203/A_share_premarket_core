from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.features.pit_signal_store import build_pit_signal_snapshot


if __name__ == "__main__":
    build_pit_signal_snapshot(ROOT)
