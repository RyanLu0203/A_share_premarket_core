from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.engineering_panel import rebuild_stage6c_from_engineering_panel


if __name__ == "__main__":
    raise SystemExit(0 if rebuild_stage6c_from_engineering_panel(ROOT) else 1)
