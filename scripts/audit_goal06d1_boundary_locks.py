from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.models.goal06d1 import audit_goal06d1_boundary_locks


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal06d1_boundary_locks(ROOT) else 1)
