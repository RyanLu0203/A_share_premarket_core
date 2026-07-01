from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STABLE_COMMIT = "310559ae18bbf203e795c1d66bc7181a6b11c14a"
SOURCE_BRANCH = "codex/cloakbrowser-reference-tagging"
PROJECT_CURRENT_BRANCH = "project-current"
CHECKPOINT_BRANCH = "checkpoint/arch03-stable-310559"
CHECKPOINT_TAG = "checkpoint-arch03-stable-310559"
USER_PRIVATE_BUNDLE_PATH = Path("/Users/luxinyu/Desktop/A_share_premarket_core_checkpoint_310559.bundle")
REPORT_PATH = ROOT / "outputs/audits/goal_repository_checkpoint01_audit.md"

FORBIDDEN_OUTPUT_PARTS = {
    "dashboard",
    "frontend",
    "streamlit",
    "html",
    "orders",
    "broker",
    "trading",
    "paper_trading",
    "live_trading",
    "production",
    "local_lake",
    "factor_mining",
    "dqn",
    "rl",
}


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    _check_source_branch(failures)
    _check_refs(failures, warnings)
    _check_docs(failures)
    _check_workflow_locks(failures)
    _check_forbidden_paths(failures)
    _check_file_sizes(failures)
    _check_bundle(warnings)

    status = "PASS" if not failures else "BLOCKED"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# GOAL-REPOSITORY-CHECKPOINT-01 Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Stable commit: `{STABLE_COMMIT}`",
                f"Source branch: `{SOURCE_BRANCH}`",
                f"Project current branch: `{PROJECT_CURRENT_BRANCH}`",
                f"Frozen checkpoint branch: `{CHECKPOINT_BRANCH}`",
                f"Annotated tag: `{CHECKPOINT_TAG}`",
                f"User-private bundle path: `{USER_PRIVATE_BUNDLE_PATH}`",
                "Bundle status: user-private backup only; not a Codex Max input, onboarding dependency, or validation dependency.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return 0 if not failures else 1


def _check_source_branch(failures: list[str]) -> None:
    local_source_ref = _first_local_ref(SOURCE_BRANCH)
    if not local_source_ref:
        failures.append(f"source branch missing locally/remotely fetched: {SOURCE_BRANCH}")
    elif not _git_ok(["merge-base", "--is-ancestor", STABLE_COMMIT, local_source_ref]):
        failures.append(f"source branch does not contain stable commit: {local_source_ref}")
    remote = _remote_ref(f"refs/heads/{SOURCE_BRANCH}")
    if not remote:
        failures.append(f"source branch missing remotely: {SOURCE_BRANCH}")
    elif local_source_ref and not _git_ok(["merge-base", "--is-ancestor", STABLE_COMMIT, local_source_ref]):
        failures.append(f"remote source branch does not contain stable commit: {SOURCE_BRANCH}")


def _check_refs(failures: list[str], warnings: list[str]) -> None:
    checkpoint_local_ref = _first_local_ref(CHECKPOINT_BRANCH)
    checkpoint_local = _git(["rev-parse", checkpoint_local_ref]) if checkpoint_local_ref else ""
    checkpoint_remote = _remote_ref(f"refs/heads/{CHECKPOINT_BRANCH}")
    if checkpoint_local and checkpoint_local != STABLE_COMMIT:
        failures.append(f"local checkpoint branch target mismatch: {checkpoint_local}")
    if not checkpoint_local and not checkpoint_remote:
        failures.append(f"checkpoint branch missing locally/remotely: {CHECKPOINT_BRANCH}")
    if checkpoint_remote != STABLE_COMMIT:
        failures.append(f"remote checkpoint branch target mismatch: {checkpoint_remote}")

    tag_local = _git(["rev-parse", f"{CHECKPOINT_TAG}^{{}}"])
    tag_remote = _remote_ref(f"refs/tags/{CHECKPOINT_TAG}^{{}}")
    if tag_local and tag_local != STABLE_COMMIT:
        failures.append(f"local checkpoint tag target mismatch: {tag_local}")
    if not tag_local and not tag_remote:
        failures.append(f"checkpoint tag missing locally/remotely: {CHECKPOINT_TAG}")
    if tag_remote != STABLE_COMMIT:
        failures.append(f"remote checkpoint tag target mismatch: {tag_remote}")

    project_local_ref = _first_local_ref(PROJECT_CURRENT_BRANCH)
    project_local = _git(["rev-parse", project_local_ref]) if project_local_ref else ""
    project_remote = _remote_ref(f"refs/heads/{PROJECT_CURRENT_BRANCH}")
    for label, target in [("local", project_local), ("remote", project_remote)]:
        if not target:
            failures.append(f"{label} project-current branch missing")
        elif target == STABLE_COMMIT:
            warnings.append(f"{label} project-current still points to stable commit; fast-forward after governance docs commit is expected")
        elif not _git_ok(["merge-base", "--is-ancestor", STABLE_COMMIT, target]):
            failures.append(f"{label} project-current does not contain stable commit: {target}")


def _check_docs(failures: list[str]) -> None:
    required_files = [
        "CODEX.md",
        "PROJECT_STATE.md",
        "ROADMAP.md",
        "docs/governance/REPOSITORY_CHECKPOINTS.md",
        "docs/governance/CODEX_MAX_ENTRYPOINT.md",
        "docs/governance/ROLLBACK_PLAYBOOK.md",
        "outputs/audits/current_project_snapshot.md",
        "outputs/audits/current_project_snapshot.json",
        "outputs/audits/goal_repository_checkpoint01_report.md",
        "outputs/audits/goal_repository_checkpoint01_manifest.json",
        "outputs/audits/goal_repository_checkpoint01_git_refs.csv",
    ]
    for file_name in required_files:
        if not (ROOT / file_name).exists():
            failures.append(f"required checkpoint file missing: {file_name}")

    code = _read("CODEX.md")
    for text in [PROJECT_CURRENT_BRANCH, CHECKPOINT_BRANCH, CHECKPOINT_TAG, STABLE_COMMIT, "Codex Max"]:
        if text not in code:
            failures.append(f"CODEX.md missing checkpoint marker: {text}")
    if "must not start from stale main" not in code:
        failures.append("CODEX.md missing stale-main warning")

    project_state = _read("PROJECT_STATE.md")
    for text in [STABLE_COMMIT, "ready factor count remains 0", "Regime01 implemented", "Arch03 implemented", "AKShare source catalog 70 rows"]:
        if text not in project_state:
            failures.append(f"PROJECT_STATE.md missing checkpoint marker: {text}")

    roadmap = _read("ROADMAP.md")
    for text in ["GOAL-CODEX-OPERATING-SYSTEM-01", "GOAL-DATA-EXPANSION-RESEARCH-01", "GOAL-QUANT-RESEARCH-04", "locked downstream"]:
        if text not in roadmap:
            failures.append(f"ROADMAP.md missing checkpoint roadmap marker: {text}")


def _check_workflow_locks(failures: list[str]) -> None:
    path = ROOT / "configs/project/workflow_status.csv"
    rows = {row["workflow_id"]: row for row in csv.DictReader(path.open(newline="", encoding="utf-8"))}
    checkpoint = rows.get("goal_repository_checkpoint01_arch03_stable_snapshot_and_codex_max_entrypoint_gate", {})
    if checkpoint.get("status") != "implemented_governance_only":
        failures.append("GOAL-REPOSITORY-CHECKPOINT-01 workflow row is not implemented_governance_only")
    for workflow_id in [
        "goal_data_expansion_research01_market_regime_data_expansion_gate",
        "goal_quant_research04_regime_conditional_factor_evaluation_gate",
        "goal_rec_tiering01_recommendation_score_tiering_gate",
        "goal10b4_recommendation_backtest_revalidation",
        "goal_position_band_validation01_position_band_validation_gate",
        "goal10d_backtest_failure_attribution_gate",
        "dashboard_daily_report",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        row = rows.get(workflow_id, {})
        if row.get("status") not in {"locked_future", "planned_locked", "deleted_from_active_mainline"}:
            failures.append(f"downstream workflow unlocked unexpectedly: {workflow_id}={row.get('status')}")
        if row.get("implemented_in_repo") == "true":
            failures.append(f"downstream workflow marked implemented unexpectedly: {workflow_id}")


def _check_forbidden_paths(failures: list[str]) -> None:
    changed = _git(["diff", "--name-only", "HEAD"])
    staged = _git(["diff", "--cached", "--name-only"])
    names = set((changed + "\n" + staged).splitlines())
    allowed_governance = {
        "docs/governance",
        "outputs/audits",
        "outputs/diagnostics",
        "configs/project",
        "src/ashare_premarket",
        "scripts",
        "CODEX.md",
        "PROJECT_STATE.md",
        "ROADMAP.md",
        "README.md",
        "CHANGELOG.md",
        "docs/09_STEP_ITERATION_LOG.md",
    }
    for name in names:
        if not name:
            continue
        parts = set(Path(name).parts)
        if parts & FORBIDDEN_OUTPUT_PARTS and not name.startswith("outputs/audits/"):
            failures.append(f"forbidden output path changed: {name}")
        if name.endswith((".html", ".htm")):
            failures.append(f"dashboard/frontend artifact created: {name}")
        if not any(name == allowed or name.startswith(allowed + "/") for allowed in allowed_governance):
            if name.startswith("outputs/") and not name.startswith("outputs/audits/"):
                failures.append(f"unexpected non-audit output changed: {name}")


def _check_file_sizes(failures: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.stat().st_size >= 95 * 1024 * 1024:
            failures.append(f"file exceeds 95 MiB policy: {path.relative_to(ROOT)}")


def _check_bundle(warnings: list[str]) -> None:
    if not USER_PRIVATE_BUNDLE_PATH.exists():
        warnings.append(f"user-private bundle not visible from this environment: {USER_PRIVATE_BUNDLE_PATH}")
        return
    result = subprocess.run(["git", "bundle", "verify", str(USER_PRIVATE_BUNDLE_PATH)], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        warnings.append("user-private git bundle verify failed")


def _remote_ref(ref: str) -> str:
    result = subprocess.run(["git", "ls-remote", "origin", ref], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        return ""
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == ref:
            return parts[0]
    return ""


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def _first_local_ref(ref_name: str) -> str:
    for candidate in [ref_name, f"origin/{ref_name}"]:
        if _git_ok(["rev-parse", "--verify", candidate]):
            return candidate
    return ""


def _git_ok(args: list[str]) -> bool:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def _read(path: str) -> str:
    file_path = ROOT / path
    return file_path.read_text(encoding="utf-8") if file_path.exists() else ""


if __name__ == "__main__":
    raise SystemExit(main())
