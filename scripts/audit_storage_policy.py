from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.storage.policy import audit_storage_policy


if __name__ == "__main__":
    raise SystemExit(0 if audit_storage_policy(ROOT) else 1)
