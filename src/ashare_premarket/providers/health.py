from __future__ import annotations

import importlib.util


def optional_provider_import_health(provider_module: str) -> dict[str, object]:
    spec = importlib.util.find_spec(provider_module)
    return {
        "provider_module": provider_module,
        "import_available": spec is not None,
        "inspection_level": "import_spec_only",
        "live_data_fetch_performed": False,
    }

