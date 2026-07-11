from __future__ import annotations

import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any


SNAPSHOT_ROOT = "outputs/research/premarket_position_management"
LATEST_POINTER = f"{SNAPSHOT_ROOT}/latest_manifest.json"
CANONICAL_MARKET = "outputs/research/goal_premarket_portfolio_risk_management01_canonical_market_data.csv"
PROVIDER_PANEL = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"


class CommittedEvidenceStore:
    """Root-confined, cached reader used only with fixed internal evidence paths."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    @lru_cache(maxsize=None)
    def csv(self, relative_path: str) -> tuple[dict[str, str], ...]:
        path = self._path(relative_path)
        if not path.exists():
            return ()
        with path.open(newline="", encoding="utf-8") as handle:
            return tuple(dict(row) for row in csv.DictReader(handle))

    @lru_cache(maxsize=None)
    def json(self, relative_path: str) -> dict[str, Any]:
        path = self._path(relative_path)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @lru_cache(maxsize=1)
    def snapshot_dates(self) -> tuple[str, ...]:
        base = self._path(SNAPSHOT_ROOT)
        if not base.exists():
            return ()
        return tuple(
            sorted(
                child.name
                for child in base.iterdir()
                if child.is_dir() and (child / "manifest.json").exists()
            )
        )

    def latest_snapshot_date(self) -> str:
        pointer = self.json(LATEST_POINTER)
        selected = str(pointer.get("snapshot_date", ""))
        if selected in self.snapshot_dates():
            return selected
        return self.snapshot_dates()[-1] if self.snapshot_dates() else ""

    def snapshot_manifest(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.latest_snapshot_date()
        if selected not in self.snapshot_dates():
            raise KeyError(f"unknown snapshot date: {selected}")
        return self.json(f"{SNAPSHOT_ROOT}/{selected}/manifest.json")

    def snapshot_csv(self, filename: str, snapshot_date: str | None = None) -> tuple[dict[str, str], ...]:
        selected = snapshot_date or self.latest_snapshot_date()
        if selected not in self.snapshot_dates():
            raise KeyError(f"unknown snapshot date: {selected}")
        return self.csv(f"{SNAPSHOT_ROOT}/{selected}/{filename}")

    def verify_snapshot(self, snapshot_date: str | None = None) -> tuple[bool, list[str]]:
        manifest = self.snapshot_manifest(snapshot_date)
        selected = str(manifest["snapshot_date"])
        failures: list[str] = []
        for filename, expected in sorted(dict(manifest.get("checksums", {})).items()):
            path = self._path(f"{SNAPSHOT_ROOT}/{selected}/{filename}")
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"
            if actual != expected:
                failures.append(filename)
        return not failures, failures

    @lru_cache(maxsize=1)
    def canonical_rows(self) -> tuple[dict[str, str], ...]:
        return self.csv(CANONICAL_MARKET)

    @lru_cache(maxsize=1)
    def provider_panel_rows(self) -> tuple[dict[str, str], ...]:
        return self.csv(PROVIDER_PANEL)

    @lru_cache(maxsize=1)
    def canonical_dates(self) -> tuple[str, ...]:
        return tuple(sorted({row["trade_date"] for row in self.canonical_rows()}))

    def _path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError("evidence path escaped repository root")
        return candidate
