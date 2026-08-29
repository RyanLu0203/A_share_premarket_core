"""Offline ingress contracts for future liquidity evidence handoff artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Mapping

from ashare_premarket.providers.liquidity_schema_smoke_plan import (
    SANITIZED_METADATA_FIELDS,
    evaluate_observed_field_names,
    schema_smoke_calls,
    validate_sanitized_metadata,
)
from ashare_premarket.research.liquidity_candidate_source_contract import (
    REQUIRED_FIELDS,
    CandidateSourceDecision,
    evaluate_candidate_source,
)


GOAL_ID = "GOAL-LIQUIDITY-EXTERNAL-HANDOFF-READINESS-01"
MAX_CANDIDATE_ROWS = 5000
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

PREFIX = "outputs/providers/goal_liquidity_external_handoff_readiness01_"
PREFLIGHT_OUTPUT = PREFIX + "preflight.csv"
CONTRACT_OUTPUT = PREFIX + "artifact_contract.csv"
REPORT = "outputs/audits/goal_liquidity_external_handoff_readiness01_report.md"
MANIFEST = "outputs/audits/goal_liquidity_external_handoff_readiness01_manifest.json"
AUDIT = "outputs/audits/goal_liquidity_external_handoff_readiness01_audit.md"


class LiquidityHandoffError(ValueError):
    """An external handoff artifact failed a fail-closed ingress contract."""


def validate_candidate_bundle_file(
    path: Path,
    *,
    expected_sha256: str,
    source_class: str,
    decision_cutoff: str,
    repository_root: Path,
) -> CandidateSourceDecision:
    """Validate an explicit external candidate CSV without copying it into Git."""

    resolved = _external_regular_file(path, repository_root)
    _expected_hash(expected_sha256)
    if resolved.stat().st_size > 2_000_000:
        raise LiquidityHandoffError("CANDIDATE_BUNDLE_SIZE_EXCEEDED")
    if _sha256(resolved) != expected_sha256:
        raise LiquidityHandoffError("CANDIDATE_BUNDLE_CHECKSUM_MISMATCH")
    with resolved.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(REQUIRED_FIELDS):
            raise LiquidityHandoffError("CANDIDATE_BUNDLE_HEADER_MISMATCH")
        rows = list(reader)
    if len(rows) > MAX_CANDIDATE_ROWS:
        raise LiquidityHandoffError("CANDIDATE_BUNDLE_ROW_BUDGET_EXCEEDED")
    return evaluate_candidate_source(
        rows,
        source_class=source_class,
        decision_cutoff=decision_cutoff,
    )


def validate_schema_observation_file(
    path: Path,
    *,
    expected_sha256: str,
    repository_root: Path,
) -> dict[str, object]:
    """Validate one exact four-observation sanitized JSON handoff.

    A passing bundle becomes eligible for explicit review only. The importer
    cannot prove provider provenance and therefore never sets live schema
    verification or authorizes another call.
    """

    resolved = _external_regular_file(path, repository_root)
    _expected_hash(expected_sha256)
    if resolved.stat().st_size > 100_000:
        raise LiquidityHandoffError("SCHEMA_OBSERVATION_SIZE_EXCEEDED")
    if _sha256(resolved) != expected_sha256:
        raise LiquidityHandoffError("SCHEMA_OBSERVATION_CHECKSUM_MISMATCH")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LiquidityHandoffError("SCHEMA_OBSERVATION_INVALID_JSON") from exc
    if not isinstance(payload, list) or len(payload) != 4:
        raise LiquidityHandoffError("SCHEMA_OBSERVATION_EXACT_FOUR_REQUIRED")

    plan = {str(call["call_id"]): call for call in schema_smoke_calls()}
    observed: dict[str, Mapping[str, object]] = {}
    for item in payload:
        if not isinstance(item, Mapping) or not validate_sanitized_metadata(item):
            raise LiquidityHandoffError("SCHEMA_OBSERVATION_UNSANITIZED_METADATA")
        call_id = str(item["call_id"])
        if call_id not in plan or call_id in observed:
            raise LiquidityHandoffError("SCHEMA_OBSERVATION_SCOPE_MISMATCH")
        call = plan[call_id]
        for field in ("provider", "endpoint", "canonical_symbol", "provider_symbol"):
            if item[field] != call[field]:
                raise LiquidityHandoffError("SCHEMA_OBSERVATION_IDENTITY_MISMATCH")
        if (
            item["attempted"] is not True
            or item["call_count"] != 1
            or item["retry_count"] != 0
            or item["status"] != "PASS"
            or item["failure_code"] != "NONE"
            or item["observed_row_count"] < 1
        ):
            raise LiquidityHandoffError("SCHEMA_OBSERVATION_NOT_COMPLETE_PASS")
        field_result = evaluate_observed_field_names(
            str(item["provider"]), item["observed_field_names"]
        )
        if field_result["missing_field_names"] or field_result["unexpected_field_names"]:
            raise LiquidityHandoffError("SCHEMA_OBSERVATION_FIELD_SET_MISMATCH")
        observed[call_id] = item

    if set(observed) != set(plan):
        raise LiquidityHandoffError("SCHEMA_OBSERVATION_SCOPE_MISMATCH")
    return {
        "status": "PASS_REVIEW_ELIGIBLE_PROVENANCE_UNVERIFIED",
        "observation_count": 4,
        "total_call_count": 4,
        "total_retry_count": 0,
        "live_schema_verified": False,
        "provider_calls_authorized": False,
        "raw_values_persisted": False,
    }


def artifact_contract_rows() -> list[dict[str, object]]:
    return [
        {
            "artifact_type": "candidate_universe_csv",
            "outside_tracked_tree": "true",
            "checksum_required": "sha256",
            "row_rule": "100_to_5000_input_rows_exact_100_selected",
            "schema_rule": ";".join(REQUIRED_FIELDS),
            "acceptance_state": "CONTRACT_READY_NO_BUNDLE",
        },
        {
            "artifact_type": "schema_smoke_sanitized_json",
            "outside_tracked_tree": "true",
            "checksum_required": "sha256",
            "row_rule": "exactly_4_observations_zero_retries",
            "schema_rule": ";".join(SANITIZED_METADATA_FIELDS),
            "acceptance_state": "CONTRACT_READY_NO_BUNDLE",
        },
    ]


def run_goal(root: Path) -> bool:
    contracts = artifact_contract_rows()
    preflight = {
        "goal_status": "PASS_WITH_WARNINGS",
        "candidate_ingress_state": "CONTRACT_READY_NO_BUNDLE",
        "schema_observation_ingress_state": "CONTRACT_READY_NO_BUNDLE",
        "external_artifacts_accepted": 0,
        "accepted_candidate_symbols": 0,
        "accepted_schema_observations": 0,
        "provider_calls_authorized": "false",
        "provider_calls_performed": "false",
        "live_schema_verified": "false",
        "factor_construction_unlocked": "false",
        "downstream_unlock": "false",
        "next_action": "external_checksummed_bundle_or_explicit_smoke_authority",
    }
    _write_csv(root / CONTRACT_OUTPUT, contracts)
    _write_csv(root / PREFLIGHT_OUTPUT, [preflight])
    (root / REPORT).write_text(
        "\n".join(
            [
                f"# {GOAL_ID}",
                "",
                "Status: `PASS_WITH_WARNINGS`; external handoff preflight `BLOCKED`.",
                "",
                "The repository can now validate an external checksummed 100-symbol "
                "candidate CSV and an exact four-observation sanitized schema-smoke "
                "JSON without copying either source artifact into Git.",
                "",
                "No external bundle is present or accepted. Imported schema metadata "
                "cannot prove provider provenance by itself, so live schema verification "
                "remains false. No provider call or downstream unlock occurred.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    outputs = [CONTRACT_OUTPUT, PREFLIGHT_OUTPUT]
    manifest = {
        "goal_id": GOAL_ID,
        "goal_status": "PASS_WITH_WARNINGS",
        "candidate_ingress_state": "CONTRACT_READY_NO_BUNDLE",
        "schema_observation_ingress_state": "CONTRACT_READY_NO_BUNDLE",
        "external_artifacts_accepted": 0,
        "accepted_candidate_symbols": 0,
        "accepted_schema_observations": 0,
        "provider_calls_authorized": False,
        "provider_calls_performed": False,
        "live_schema_verified": False,
        "factor_construction_unlocked": False,
        "downstream_unlock": False,
        "outputs": {path: _sha256(root / path) for path in outputs},
    }
    manifest_path = root / MANIFEST
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return audit_goal(root)


def audit_goal(root: Path) -> bool:
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        valid = (
            manifest["goal_status"] == "PASS_WITH_WARNINGS"
            and manifest["candidate_ingress_state"] == "CONTRACT_READY_NO_BUNDLE"
            and manifest["schema_observation_ingress_state"]
            == "CONTRACT_READY_NO_BUNDLE"
            and manifest["external_artifacts_accepted"] == 0
            and manifest["accepted_candidate_symbols"] == 0
            and manifest["accepted_schema_observations"] == 0
            and not manifest["provider_calls_authorized"]
            and not manifest["provider_calls_performed"]
            and not manifest["live_schema_verified"]
            and not manifest["factor_construction_unlocked"]
            and not manifest["downstream_unlock"]
            and all(_sha256(root / path) == digest for path, digest in manifest["outputs"].items())
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        valid = False
    audit_path = root / AUDIT
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        "# GOAL-LIQUIDITY-EXTERNAL-HANDOFF-READINESS-01 Audit\n\n"
        f"Status: `{'PASS' if valid else 'FAIL'}`.\n",
        encoding="utf-8",
    )
    return valid


def _external_regular_file(path: Path, repository_root: Path) -> Path:
    if not path.is_absolute():
        raise LiquidityHandoffError("EXPLICIT_ABSOLUTE_EXTERNAL_PATH_REQUIRED")
    if path.is_symlink():
        raise LiquidityHandoffError("EXTERNAL_REGULAR_FILE_REQUIRED")
    resolved = path.resolve(strict=True)
    root = repository_root.resolve(strict=True)
    local_boundary = root / ".local"
    inside_repository = resolved == root or root in resolved.parents
    inside_local_boundary = resolved == local_boundary or local_boundary in resolved.parents
    if inside_repository and not inside_local_boundary:
        raise LiquidityHandoffError("TRACKED_REPOSITORY_PATH_FORBIDDEN")
    if not resolved.is_file():
        raise LiquidityHandoffError("EXTERNAL_REGULAR_FILE_REQUIRED")
    return resolved


def _expected_hash(value: str) -> None:
    if not SHA256_PATTERN.fullmatch(value):
        raise LiquidityHandoffError("EXPLICIT_SHA256_REQUIRED")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
