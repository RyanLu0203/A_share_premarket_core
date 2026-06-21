from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.storage.policy import audit_data_bundle_manifest


if __name__ == "__main__":
    raise SystemExit(0 if audit_data_bundle_manifest(ROOT) else 1)
