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

    def latest_snapshot_date(self, max_date: str | None = None) -> str:
        return str(self.resolve_snapshot(max_date=max_date)["selected_date"])

    def snapshot_date_at_or_before(self, value: str) -> str:
        return self.latest_snapshot_date(max_date=value)

    def resolve_snapshot(
        self,
        requested_date: str | None = None,
        *,
        max_date: str | None = None,
        replay: bool = False,
    ) -> dict[str, Any]:
        dates = tuple(date for date in self.snapshot_dates() if not max_date or date <= max_date)
        if not dates:
            raise KeyError("no snapshot is available for the requested boundary")
        latest_discovered = dates[-1]
        pointer = self._pointer_status()

        if requested_date:
            if requested_date not in self.snapshot_dates():
                raise KeyError(f"unknown snapshot date: {requested_date}")
            if max_date and requested_date > max_date:
                raise ValueError("requested snapshot is after the live target boundary")
            verified, failures = self.verify_snapshot(requested_date)
            if not verified:
                raise ValueError(f"requested snapshot checksum validation failed: {','.join(failures)}")
            return {
                "selected_date": requested_date,
                "requested_date": requested_date,
                "latest_discovered_date": self.snapshot_dates()[-1],
                "pointer_date": pointer["snapshot_date"],
                "resolution_status": "HISTORICAL_REPLAY_VERIFIED" if replay else "EXPLICIT_SNAPSHOT_VERIFIED",
                "integrity": "VERIFIED",
                "stale": requested_date != self.snapshot_dates()[-1],
                "system_blocking": False,
                "warnings": [],
            }

        verified_dates = []
        failures_by_date: dict[str, list[str]] = {}
        for candidate in dates:
            verified, failures = self.verify_snapshot(candidate)
            if verified:
                verified_dates.append(candidate)
            else:
                failures_by_date[candidate] = failures
        if not verified_dates:
            raise ValueError("no checksum-verified snapshot is available")
        latest_verified = verified_dates[-1]

        if latest_verified != latest_discovered:
            return {
                "selected_date": latest_verified,
                "requested_date": "",
                "latest_discovered_date": latest_discovered,
                "pointer_date": pointer["snapshot_date"],
                "resolution_status": "LATEST_INVALID_RESEARCH_FALLBACK",
                "integrity": "VERIFIED",
                "stale": True,
                "system_blocking": True,
                "warnings": [
                    f"LATEST_SNAPSHOT_CHECKSUM_INVALID:{latest_discovered}:{','.join(failures_by_date[latest_discovered])}"
                ],
            }

        pointer_current = pointer["verified"] and pointer["snapshot_date"] == latest_verified
        if pointer_current:
            status = "CURRENT_VERIFIED"
            warnings: list[str] = []
        elif pointer["verified"]:
            status = "POINTER_STALE_RECOVERED"
            warnings = [f"STALE_SNAPSHOT_POINTER:{pointer['snapshot_date']}->{latest_verified}"]
        else:
            status = "POINTER_INVALID_RECOVERED"
            warnings = [f"INVALID_SNAPSHOT_POINTER:{pointer['reason']}"]
        return {
            "selected_date": latest_verified,
            "requested_date": "",
            "latest_discovered_date": latest_discovered,
            "pointer_date": pointer["snapshot_date"],
            "resolution_status": status,
            "integrity": "VERIFIED",
            "stale": False,
            "system_blocking": False,
            "warnings": warnings,
        }

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
        requested = snapshot_date or self.latest_snapshot_date()
        manifest = self.snapshot_manifest(requested)
        selected = str(manifest.get("snapshot_date", ""))
        failures: list[str] = []
        if selected != requested:
            failures.append("manifest_snapshot_date")
        checksums = dict(manifest.get("checksums", {}))
        if not checksums:
            failures.append("missing_checksums")
        for filename, expected in sorted(checksums.items()):
            if Path(filename).name != filename:
                failures.append(filename)
                continue
            path = self._path(f"{SNAPSHOT_ROOT}/{requested}/{filename}")
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
            immutable_path = self._path(
                f"outputs/research/daily_incremental_evidence_refresh/{snapshot_date}/refresh_manifest.json"
            )
            if immutable_path.exists():
                payload = json.loads(immutable_path.read_text(encoding="utf-8"))
                payload["refresh_manifest_path"] = immutable_path.relative_to(self.root).as_posix()
                payload["refresh_manifest_integrity"] = self._verify_immutable_refresh(payload)
                return payload
        payload = self._json_uncached(DAILY_REFRESH_LATEST)
        immutable_path, immutable = self._latest_immutable_refresh()
        if immutable_path and str(immutable.get("target_trading_date", "")) > str(payload.get("target_trading_date", "")):
            payload = immutable
            payload["refresh_manifest_path"] = immutable_path.relative_to(self.root).as_posix()
            payload["refresh_manifest_integrity"] = self._verify_immutable_refresh(payload)
            payload["pointer_status"] = "STALE_POINTER_RECOVERED"
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
        candidates = (
            sorted(
                (child / "refresh_manifest.json" for child in base.iterdir() if child.is_dir()),
                key=lambda path: path.parent.name,
            )
            if base.exists()
            else []
        )
        for path in reversed(candidates):
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("refresh_status") == "SUCCEEDED" and self._verify_immutable_refresh(payload) == "VERIFIED":
                return path, payload
        return None, {}

    def _verify_immutable_refresh(self, payload: dict[str, Any]) -> str:
        relative = str(payload.get("snapshot_manifest_path", ""))
        expected_version = str(payload.get("snapshot_version", "")).removeprefix("sha256:")
        if not relative or len(expected_version) != 16:
            return "FAILED"
        path = self._path(relative)
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()[:16] != expected_version:
            return "FAILED"
        snapshot_date = str(payload.get("snapshot_date") or payload.get("target_trading_date", ""))
        verified, _ = self.verify_snapshot(snapshot_date)
        return "VERIFIED" if verified else "FAILED"

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

    def _pointer_status(self) -> dict[str, Any]:
        pointer = self._json_uncached(LATEST_POINTER)
        selected = str(pointer.get("snapshot_date", ""))
        expected_path = f"{SNAPSHOT_ROOT}/{selected}/manifest.json" if selected else ""
        relative = str(pointer.get("snapshot_manifest_path", ""))
        expected_checksum = str(pointer.get("snapshot_manifest_checksum", ""))
        if not selected or not relative or not expected_checksum:
            return {"verified": False, "snapshot_date": selected, "reason": "MISSING_POINTER_FIELDS"}
        if relative != expected_path:
            return {"verified": False, "snapshot_date": selected, "reason": "POINTER_PATH_MISMATCH"}
        path = self._path(relative)
        if not path.exists():
            return {"verified": False, "snapshot_date": selected, "reason": "POINTER_TARGET_MISSING"}
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_checksum:
            return {"verified": False, "snapshot_date": selected, "reason": "POINTER_CHECKSUM_MISMATCH"}
        verified, failures = self.verify_snapshot(selected)
        return {
            "verified": verified,
            "snapshot_date": selected,
            "reason": "" if verified else f"SNAPSHOT_CHECKSUM_MISMATCH:{','.join(failures)}",
        }
