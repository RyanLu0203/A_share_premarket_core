from __future__ import annotations

import json
from pathlib import Path

SWITCH_CONFIG = "configs/providers/browser_provider_switches.yaml"


def load_browser_provider_switches(root: Path) -> dict[str, object]:
    return json.loads((root / SWITCH_CONFIG).read_text(encoding="utf-8"))


def browser_provider_project_default(root: Path) -> bool:
    switches = load_browser_provider_switches(root)
    provider = switches.get("browser_assisted_provider", {})
    return str(provider.get("project_default", "disabled")) == "enabled"
