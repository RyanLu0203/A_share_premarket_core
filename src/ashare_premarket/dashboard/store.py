from __future__ import annotations

import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any


SNAPSHOT_ROOT = "outputs/research/premarket_position_management"
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
        dates = self.snapshot_dates()
        return dates[-1] if dates else ""

    def snapshot_date_at_or_before(self, value: str) -> str:
        eligible = tuple(date for date in self.snapshot_dates() if date <= value)
        return eligible[-1] if eligible else ""

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

    def refresh_status(self, snapshot_date: str | None = None) -> dict[str, Any]:
        if snapshot_date:
            path = self._path(f"outputs/research/daily_incremental_evidence_refresh/{snapshot_date}/refresh_manifest.json")
            if path.exists():
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["refresh_manifest_path"] = path.relative_to(self.root).as_posix()
                payload["refresh_manifest_integrity"] = self._verify_immutable_refresh(payload)
                return payload
        payload = self._json_uncached(DAILY_REFRESH_LATEST)
        immutable_path, immutable = self._latest_immutable_refresh()
        if immutable_path and str(immutable.get("target_trading_date", "")) > str(payload.get("target_trading_date", "")):
            payload = immutable
            payload["refresh_manifest_path"] = immutable_path.relative_to(self.root).as_posix()
            payload["refresh_manifest_integrity"] = self._verify_immutable_refresh(payload)
            return payload
        relative = str(payload.get("refresh_manifest_path", ""))
        expected = str(payload.get("refresh_manifest_checksum", ""))
        if not relative or not expected:
            payload["refresh_manifest_integrity"] = "UNAVAILABLE"
            return payload
        path = self._path(relative)
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"
        payload["refresh_manifest_integrity"] = "VERIFIED" if actual == expected else "FAILED"
        return payload

    def _latest_immutable_refresh(self) -> tuple[Path | None, dict[str, Any]]:
        base = self._path("outputs/research/daily_incremental_evidence_refresh")
        candidates = sorted(
            (child / "refresh_manifest.json" for child in base.iterdir() if child.is_dir()),
            key=lambda path: path.parent.name,
        ) if base.exists() else []
        for path in reversed(candidates):
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("refresh_status") == "SUCCEEDED":
                return path, payload
        return None, {}

    def _verify_immutable_refresh(self, payload: dict[str, Any]) -> str:
        relative = str(payload.get("snapshot_manifest_path", ""))
        expected = str(payload.get("snapshot_version", "")).removeprefix("sha256:")[:16]
        path = self._path(relative) if relative else None
        if not path or not expected or not path.exists():
            return "FAILED"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        snapshot_date = str(payload.get("snapshot_date", payload.get("target_trading_date", "")))
        verified, _ = self.verify_snapshot(snapshot_date)
        return "VERIFIED" if actual.startswith(expected) and verified else "FAILED"

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
