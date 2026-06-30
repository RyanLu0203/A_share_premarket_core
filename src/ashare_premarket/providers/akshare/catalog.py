from __future__ import annotations

import importlib
from typing import Iterable


def safe_introspect_akshare_functions(function_names: Iterable[str]) -> dict[str, str]:
    try:
        akshare = importlib.import_module("akshare")
    except Exception:
        return {name: "akshare_not_importable" for name in function_names}
    return {name: "available" if hasattr(akshare, name) else "not_found" for name in function_names}

