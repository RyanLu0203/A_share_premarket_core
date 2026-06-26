from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.contract_design.goal10a import run_goal10a_backtest_contract_design_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal10a_backtest_contract_design_gate(ROOT) else 1)
