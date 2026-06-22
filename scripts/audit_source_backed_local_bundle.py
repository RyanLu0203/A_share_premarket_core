from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.providers.ingestion import audit_source_backed_local_bundle


if __name__ == "__main__":
    raise SystemExit(0 if audit_source_backed_local_bundle(ROOT) else 1)
