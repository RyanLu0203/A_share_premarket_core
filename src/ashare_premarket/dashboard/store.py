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
DAILY_REFRESH_LATEST = "outputs/research/daily_incremental_evidence_refresh/latest_refresh.json"


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
        pointer = self._json_uncached(LATEST_POINTER)
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
        canonical_path = str(manifest.get("canonical_evidence_path", ""))
        canonical_checksum = str(manifest.get("canonical_evidence_checksum", ""))
        if canonical_path and canonical_checksum:
            path = self._path(canonical_path)
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"
            if actual != canonical_checksum:
                failures.append("canonical_evidence")
        return not failures, failures

    def canonical_rows(self, snapshot_date: str | None = None) -> tuple[dict[str, str], ...]:
        selected = snapshot_date or self.latest_snapshot_date()
        manifest = self.snapshot_manifest(selected) if selected else {}
        relative = str(manifest.get("canonical_evidence_path") or CANONICAL_MARKET)
        expected = str(manifest.get("canonical_evidence_checksum", ""))
        path = self._path(relative)
        if expected:
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"
            if actual != expected:
                raise ValueError("canonical evidence checksum mismatch")
        return self.csv(relative)

    @lru_cache(maxsize=1)
    def provider_panel_rows(self) -> tuple[dict[str, str], ...]:
        return self.csv(PROVIDER_PANEL)

    def canonical_dates(self, snapshot_date: str | None = None) -> tuple[str, ...]:
        return tuple(sorted({row["trade_date"] for row in self.canonical_rows(snapshot_date)}))

    def refresh_status(self) -> dict[str, Any]:
        payload = self._json_uncached(DAILY_REFRESH_LATEST)
        relative = str(payload.get("refresh_manifest_path", ""))
        expected = str(payload.get("refresh_manifest_checksum", ""))
        if not relative or not expected:
            payload["refresh_manifest_integrity"] = "UNAVAILABLE"
            return payload
        path = self._path(relative)
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"
        payload["refresh_manifest_integrity"] = "VERIFIED" if actual == expected else "FAILED"
        return payload

    def snapshot_version(self, snapshot_date: str | None = None) -> str:
        selected = snapshot_date or self.latest_snapshot_date()
        manifest_path = self._path(f"{SNAPSHOT_ROOT}/{selected}/manifest.json")
        if not selected or not manifest_path.exists():
            return ""
        return f"sha256:{hashlib.sha256(manifest_path.read_bytes()).hexdigest()[:16]}"

    def _path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError("evidence path escaped repository root")
        return candidate

    def _json_uncached(self, relative_path: str) -> dict[str, Any]:
        path = self._path(relative_path)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
