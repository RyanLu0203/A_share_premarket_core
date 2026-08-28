from _bootstrap import ROOT
from ashare_premarket.providers.liquidity_evidence_foundation import audit_foundation
if __name__=="__main__":raise SystemExit(0 if audit_foundation(ROOT) else 1)
