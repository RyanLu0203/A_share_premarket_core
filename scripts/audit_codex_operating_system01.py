from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "outputs/audits/goal_codex_operating_system01_audit.md"

AUTHORITATIVE_REMOTE_REPOSITORY = "RyanLu0203/A_share_premarket_core"
AUTHORITATIVE_REMOTE_BRANCH = "project-current"
LATEST_CONFIRMED_REMOTE_COMMIT = "e216aac7cac188f401e970a03defca73b11aa449"
CHECKPOINT_BRANCH = "checkpoint/arch03-stable-310559"
CHECKPOINT_TAG = "checkpoint-arch03-stable-310559"
STABLE_ARCH03_COMMIT = "310559ae18bbf203e795c1d66bc7181a6b11c14a"

REQUIRED_GOVERNANCE_DOCS = [
    "docs/governance/NEW_CODEX_ONBOARDING.md",
    "docs/governance/CODEX_MAX_REMOTE_WINDOWS_PROTOCOL.md",
    "docs/governance/CODEX_MAX_OPERATING_PROTOCOL.md",
    "docs/governance/MAIN_CODEX_REVIEW_PROTOCOL.md",
    "docs/governance/PROJECT_AUTHORITY_MODEL.md",
    "docs/governance/GITHUB_ONLY_SOURCE_POLICY.md",
    "docs/governance/WINDOWS_COMPATIBILITY_POLICY.md",
    "docs/governance/GOAL_QUEUE.md",
    "docs/governance/GOAL_ACCEPTANCE_STANDARD.md",
    "docs/governance/DESTRUCTIVE_CHANGE_POLICY.md",
    "docs/governance/BRANCHING_AND_PR_POLICY.md",
    "docs/governance/HANDOFF_TEMPLATE.md",
    "docs/governance/LOCKED_BOUNDARIES.md",
    "docs/governance/CODEX_MAX_SMOKE_TEST_PLAN.md",
    "docs/governance/PROJECT_STATE_UPDATE_POLICY.md",
    "docs/governance/AUTHORITATIVE_STATE_FILES.md",
    "docs/governance/REMOTE_CHECKPOINT_AND_ROLLBACK_POLICY.md",
]

REQUIRED_TEMPLATES = [
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/goal_request.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/research_task.md",
    ".github/CODEOWNERS",
]

REQUIRED_OUTPUTS = [
    "outputs/audits/goal_codex_operating_system01_report.md",
    "outputs/audits/goal_codex_operating_system01_manifest.json",
    "outputs/audits/goal_codex_operating_system01_governance_inventory.csv",
    "outputs/audits/current_project_snapshot.md",
    "outputs/audits/current_project_snapshot.json",
]

LOCKED_EXPECTATIONS = {
    "goal_codex_max_onboarding_smoke01_remote_windows_github_only_compliance_gate": "locked_future",
    "goal_data_expansion_research01_market_regime_data_expansion_gate": "implemented_research_only",
    "goal_regime_label_research02_expanded_market_regime_label_refinement_gate": "implemented_research_only",
    "goal_quant_research04_regime_conditional_factor_evaluation_gate": "implemented_research_only",
    "goal_rec_tiering01_recommendation_score_tiering_gate": "locked_future",
    "goal10b4_recommendation_backtest_revalidation": "locked_future",
    "goal_position_band_validation01_position_band_validation_gate": "locked_future",
    "goal10d_backtest_failure_attribution_gate": "locked_future",
    "dashboard_daily_report": "locked_future",
    "broker_live_trading": "locked_future",
    "production_db_writes": "locked_future",
    "production_model_promotion": "locked_future",
    "portfolio_backtest": "locked_future",
    "dqn_rl_mainline": "deleted_from_active_mainline",
}


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    _check_required_files(failures)
    _check_root_markers(failures)
    _check_governance_markers(failures)
    _check_templates(failures)
    _check_workflow(failures)
    _check_outputs(failures)
    _check_bundle_language(failures)
    _check_remote_refs(warnings)
    status = "PASS" if not failures else "BLOCKED"
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(_audit_text(status, failures, warnings), encoding="utf-8")
    print(f"GOAL-CODEX-OPERATING-SYSTEM-01 audit: {status}")
    return 0 if not failures else 1


def _check_required_files(failures: list[str]) -> None:
    for file_name in [
        "CODEX.md",
        "AGENTS.md",
        "PROJECT_STATE.md",
        "ROADMAP.md",
        "configs/project/workflow_status.csv",
        *REQUIRED_GOVERNANCE_DOCS,
        *REQUIRED_TEMPLATES,
        *REQUIRED_OUTPUTS,
    ]:
        if not (ROOT / file_name).exists():
            failures.append(f"required file missing: {file_name}")


def _check_root_markers(failures: list[str]) -> None:
    code = _read("CODEX.md")
    code_normalized = _normalize(code)
    for marker in [
        AUTHORITATIVE_REMOTE_REPOSITORY,
        AUTHORITATIVE_REMOTE_BRANCH,
        LATEST_CONFIRMED_REMOTE_COMMIT,
        CHECKPOINT_BRANCH,
        CHECKPOINT_TAG,
        STABLE_ARCH03_COMMIT,
        "must not rely on owner-specific absolute macOS paths",
        "must not rely on local bundle backup",
        "GitHub-committed artifacts",
        "codex-max/<goal-id>",
        "Main Codex reviews Codex Max output",
    ]:
        if _normalize(marker) not in code_normalized:
            failures.append(f"CODEX.md missing marker: {marker}")
    agents = _read("AGENTS.md")
    for marker in [
        "GitHub-only source policy",
        "Remote-only artifact policy",
        "Windows-compatible execution policy",
        "codex-max/<goal-id>",
        "Destructive-change policy",
    ]:
        if marker not in agents:
            failures.append(f"AGENTS.md missing marker: {marker}")
    state = _read("PROJECT_STATE.md")
    for marker in [
        "Authoritative remote branch: `project-current`",
        "Ready factor count: `0`",
        "Codex Max remote Windows GitHub-only constraint",
        "GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE",
    ]:
        if marker not in state:
            failures.append(f"PROJECT_STATE.md missing marker: {marker}")
    roadmap = _read("ROADMAP.md")
    for marker in [
        "GOAL-CODEX-OPERATING-SYSTEM-01",
        "GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE",
        "GOAL-DATA-EXPANSION-RESEARCH-01",
        "GOAL-QUANT-RESEARCH-04",
        "Local bundle backup is a user-private rollback backup only",
    ]:
        if marker not in roadmap:
            failures.append(f"ROADMAP.md missing marker: {marker}")


def _check_governance_markers(failures: list[str]) -> None:
    checks = {
        "docs/governance/PROJECT_AUTHORITY_MODEL.md": [
            "User: final authority",
            "Main Codex: program brain",
            "Codex Max: high-capacity executor",
            "cannot select the next project goal independently",
        ],
        "docs/governance/GITHUB_ONLY_SOURCE_POLICY.md": [
            "GitHub is the only authoritative source for Codex Max",
            "project-current",
            "Codex Max must not rely on",
            "local bundle backups",
        ],
        "docs/governance/WINDOWS_COMPATIBILITY_POLICY.md": [
            "pathlib",
            "Do not require bash-only commands",
            "Do not require `chmod`",
            "Use UTF-8",
        ],
        "docs/governance/CODEX_MAX_REMOTE_WINDOWS_PROTOCOL.md": [
            "Clone from GitHub",
            "codex-max/<goal-id>",
            "Never push directly to `project-current`",
            "Use local Mac paths",
        ],
        "docs/governance/MAIN_CODEX_REVIEW_PROTOCOL.md": [
            "codex-max/*",
            "project-current",
            "no local Mac path dependency",
            "Windows-compatible commands and paths",
        ],
        "docs/governance/REMOTE_CHECKPOINT_AND_ROLLBACK_POLICY.md": [
            CHECKPOINT_BRANCH,
            CHECKPOINT_TAG,
            "user-private backup",
            "not part of Codex Max onboarding",
        ],
    }
    for file_name, markers in checks.items():
        text = _read(file_name)
        for marker in markers:
            if marker not in text:
                failures.append(f"{file_name} missing marker: {marker}")


def _check_templates(failures: list[str]) -> None:
    pr = _read(".github/PULL_REQUEST_TEMPLATE.md")
    for marker in [
        "Goal ID",
        "Base branch",
        "Worker branch",
        "Windows/remote environment statement",
        "Only GitHub sources used",
        "No local Mac path used",
        "No local bundle used",
        "No local-lake data used",
        "Main Codex review checklist",
    ]:
        if marker not in pr:
            failures.append(f"PR template missing marker: {marker}")
    owners = _read(".github/CODEOWNERS")
    for marker in [
        "CODEX.md",
        "AGENTS.md",
        "configs/project/workflow_status.csv",
        "docs/governance/**",
        "scripts/run_adapter_audit.py",
        "scripts/audit_repository_checkpoint01.py",
        "src/ashare_premarket/**",
        "outputs/audits/**",
    ]:
        if marker not in owners:
            failures.append(f"CODEOWNERS missing marker: {marker}")


def _check_workflow(failures: list[str]) -> None:
    path = ROOT / "configs/project/workflow_status.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    codex_os = rows.get("goal_codex_operating_system01_codex_max_governance_gate", {})
    if codex_os.get("status") != "implemented_governance_only":
        failures.append("GOAL-CODEX-OPERATING-SYSTEM-01 workflow row is not implemented_governance_only")
    for workflow_id, expected in LOCKED_EXPECTATIONS.items():
        status = rows.get(workflow_id, {}).get("status")
        if status != expected:
            failures.append(f"{workflow_id} expected {expected}, got {status}")


def _check_outputs(failures: list[str]) -> None:
    manifest_path = ROOT / "outputs/audits/goal_codex_operating_system01_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key in [
            "scientific_outputs_changed",
            "factor_classifications_changed",
            "ready_factor_count_changed",
            "downstream_goals_unlocked",
            "recommendation_outputs_created",
            "position_outputs_created",
            "dashboard_frontend_artifacts_created",
            "trading_broker_production_outputs_created",
            "local_lake_outputs_created",
            "factor_mining_outputs_created",
            "dqn_rl_outputs_created",
        ]:
            if manifest.get(key) is not False:
                failures.append(f"manifest boundary {key} expected false, got {manifest.get(key)!r}")
        if manifest.get("github_only_source_policy") is not True:
            failures.append("manifest github_only_source_policy must be true")
        if manifest.get("windows_compatible_policy") is not True:
            failures.append("manifest windows_compatible_policy must be true")
        if manifest.get("ready_factor_count") != 0:
            failures.append("manifest ready_factor_count must be 0")


def _check_bundle_language(failures: list[str]) -> None:
    for file_name in ["CODEX.md", "PROJECT_STATE.md", "ROADMAP.md", *REQUIRED_GOVERNANCE_DOCS]:
        lines = _read(file_name).splitlines()
        for lineno, line in enumerate(lines, start=1):
            lower = line.lower()
            context = _context(lines, lineno)
            if "/users/luxinyu" in lower and not _allowed_local_dependency_context(context):
                failures.append(f"{file_name}:{lineno} references local Mac path without user-private/prohibited framing")
            if "local bundle" in lower and "codex max" in context and not _allowed_local_dependency_context(context):
                failures.append(f"{file_name}:{lineno} may frame local bundle as Codex Max dependency")


def _check_remote_refs(warnings: list[str]) -> None:
    project_current = _remote_ref(f"refs/heads/{AUTHORITATIVE_REMOTE_BRANCH}")
    checkpoint = _remote_ref(f"refs/heads/{CHECKPOINT_BRANCH}")
    tag = _remote_ref(f"refs/tags/{CHECKPOINT_TAG}^{{}}")
    if not project_current:
        warnings.append("remote project-current not visible to ls-remote")
    if checkpoint != STABLE_ARCH03_COMMIT:
        warnings.append(f"remote checkpoint branch target is {checkpoint}")
    if tag != STABLE_ARCH03_COMMIT:
        warnings.append(f"remote checkpoint tag target is {tag}")


def _audit_text(status: str, failures: list[str], warnings: list[str]) -> str:
    return "\n".join(
        [
            "# GOAL-CODEX-OPERATING-SYSTEM-01 Audit",
            "",
            f"Status: `{status}`",
            "",
            f"Authoritative remote repository: `{AUTHORITATIVE_REMOTE_REPOSITORY}`",
            f"Authoritative remote branch: `{AUTHORITATIVE_REMOTE_BRANCH}`",
            f"Latest confirmed remote commit: `{LATEST_CONFIRMED_REMOTE_COMMIT}`",
            f"Checkpoint branch: `{CHECKPOINT_BRANCH}`",
            f"Checkpoint tag: `{CHECKPOINT_TAG}`",
            "",
            "## Failures",
            *[f"- {failure}" for failure in failures],
            "",
            "## Warnings",
            *[f"- {warning}" for warning in warnings],
            "",
        ]
    )


def _read(path: str) -> str:
    file_path = ROOT / path
    return file_path.read_text(encoding="utf-8") if file_path.exists() else ""


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _context(lines: list[str], lineno: int) -> str:
    start = max(0, lineno - 7)
    end = min(len(lines), lineno + 4)
    return " ".join(lines[start:end]).lower()


def _allowed_local_dependency_context(text: str) -> bool:
    return any(
        phrase in text
        for phrase in [
            "must not",
            "do not",
            "creates no",
            "not rely",
            "not part of codex max",
            "not a codex max",
            "not accessible",
            "no local bundle dependency",
            "no local mac path dependency",
            "user-private",
            "prohibited",
        ]
    )


def _remote_ref(ref: str) -> str:
    result = subprocess.run(["git", "ls-remote", "origin", ref], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        return ""
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == ref:
            return parts[0]
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
