from __future__ import annotations

import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "e216aac7cac188f401e970a03defca73b11aa449"
ALLOWED_LOCK_PROMOTIONS = {
    "goal_codex_operating_system01_codex_max_governance_gate",
    # Authorized research promotions reconciled from the Regime02 research lineage
    # (GOAL-BRANCH-LINEAGE-RECONCILIATION-01): DataExpansion01 and its downstream
    # Regime02 refinement gate are implemented research-only on project-current.
    "goal_data_expansion_research01_market_regime_data_expansion_gate",
    "goal_regime_label_research02_expanded_market_regime_label_refinement_gate",
    # Authorized research promotion (GOAL-QUANT-RESEARCH-04): regime-conditional factor
    # evaluation is implemented research-only; it keeps ready_factor_count 0 and does not
    # unlock recommendation tiering.
    "goal_quant_research04_regime_conditional_factor_evaluation_gate",
}


def main() -> int:
    failures: list[str] = []
    _check_deleted_files(failures)
    _check_workflow_rows(failures)
    _check_forbidden_outputs(failures)
    if failures:
        print("Destructive-change audit: BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Destructive-change audit: PASS")
    return 0


def _check_deleted_files(failures: list[str]) -> None:
    for line in _git(["diff", "--name-status", BASE_COMMIT, "--"]).splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        status, path = parts
        if status.startswith("D"):
            if path.startswith(("src/", "tests/", "docs/", "configs/", "outputs/audits/")) or path.startswith("scripts/"):
                failures.append(f"deleted protected file without destructive approval: {path}")


def _check_workflow_rows(failures: list[str]) -> None:
    current_path = ROOT / "configs/project/workflow_status.csv"
    base_text = _git(["show", f"{BASE_COMMIT}:configs/project/workflow_status.csv"])
    if not base_text:
        failures.append("unable to read base workflow_status.csv")
        return
    base_rows = {row["workflow_id"]: row for row in csv.DictReader(base_text.splitlines())}
    with current_path.open(newline="", encoding="utf-8") as handle:
        current_rows = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    for workflow_id in base_rows:
        if workflow_id not in current_rows:
            failures.append(f"deleted workflow row: {workflow_id}")
    for workflow_id, base_row in base_rows.items():
        current = current_rows.get(workflow_id)
        if not current:
            continue
        if base_row["status"] == "locked_future" and current["status"].startswith("implemented_"):
            if workflow_id not in ALLOWED_LOCK_PROMOTIONS:
                failures.append(f"unexpected locked_future promotion: {workflow_id}")


def _check_forbidden_outputs(failures: list[str]) -> None:
    for line in _git(["diff", "--name-status", BASE_COMMIT, "--"]).splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        status, path = parts
        lower = path.lower()
        if not status.startswith("A"):
            continue
        if lower.endswith((".html", ".htm")) or any(
            token in lower
            for token in [
                "recommendation_orders",
                "position_orders",
                "target_price",
                "order_quantity",
                "portfolio_returns",
                "equity_curve",
                "streamlit",
            ]
        ):
            failures.append(f"forbidden actionable output added: {path}")


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    return result.stdout if result.returncode == 0 else ""


if __name__ == "__main__":
    raise SystemExit(main())
