from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "outputs/audits/current_project_snapshot.md"
OUT_JSON = ROOT / "outputs/audits/current_project_snapshot.json"

AUTHORITATIVE_REMOTE_REPOSITORY = "RyanLu0203/A_share_premarket_core"
AUTHORITATIVE_REMOTE_BRANCH = "project-current"
LATEST_CONFIRMED_REMOTE_COMMIT = "e216aac7cac188f401e970a03defca73b11aa449"
CHECKPOINT_BRANCH = "checkpoint/arch03-stable-310559"
CHECKPOINT_TAG = "checkpoint-arch03-stable-310559"
STABLE_ARCH03_COMMIT = "310559ae18bbf203e795c1d66bc7181a6b11c14a"
USER_PRIVATE_LOCAL_BUNDLE_PATH = "environment:ASHARE_PRIVATE_CHECKPOINT_BUNDLE"
NEXT_SMOKE_GOAL = "GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE"


def main() -> int:
    rows = _workflow_rows()
    implemented = [
        row["stage_or_goal"]
        for row in rows
        if row["status"].startswith("implemented_")
    ]
    locked = [
        row["stage_or_goal"]
        for row in rows
        if row["status"] in {"locked_future", "planned_locked", "deleted_from_active_mainline"}
    ]
    snapshot = {
        "governance_goal": "GOAL-CODEX-OPERATING-SYSTEM-01",
        "authoritative_remote_repository": AUTHORITATIVE_REMOTE_REPOSITORY,
        "current_remote_branch": AUTHORITATIVE_REMOTE_BRANCH,
        "latest_confirmed_remote_commit": LATEST_CONFIRMED_REMOTE_COMMIT,
        "current_local_branch": _git(["branch", "--show-current"]),
        "current_local_commit": _git(["rev-parse", "HEAD"]),
        "checkpoint_branch": CHECKPOINT_BRANCH,
        "checkpoint_tag": CHECKPOINT_TAG,
        "stable_arch03_commit": STABLE_ARCH03_COMMIT,
        "local_bundle_path": USER_PRIVATE_LOCAL_BUNDLE_PATH,
        "local_bundle_status": "user_private_only_not_codex_max_dependency",
        "implemented_goals": implemented,
        "locked_future_goals": locked,
        "latest_scientific_status": "review_only_research_only_outputs_unchanged",
        "ready_factor_count": 0,
        "refined_factor_state": "GOAL-QUANT-RESEARCH-03 implemented_research_only; ready factor count 0",
        "regime_label_state": "GOAL-REGIME-LABEL-RESEARCH-01 implemented_research_only",
        "provider_catalog_state": "Provider registry network disabled by default",
        "akshare_catalog_state": "AKShare source catalog has 70 rows",
        "next_allowed_goals": [
            NEXT_SMOKE_GOAL,
            "GOAL-DATA-EXPANSION-RESEARCH-01-MARKET-REGIME-DATA-EXPANSION-GATE",
            "GOAL-QUANT-RESEARCH-04-REGIME-CONDITIONAL-FACTOR-EVALUATION-GATE after DataExpansion or explicit user approval",
        ],
        "validation_commands": [
            "python -m compileall -q .",
            "python -m pytest tests -q",
            "python scripts/audit_codex_operating_system01.py",
            "python scripts/audit_github_only_source_policy.py",
            "python scripts/audit_windows_compatibility_policy.py",
            "python scripts/audit_destructive_changes.py",
            "python scripts/run_program_validation_profile.py",
            "python scripts/run_safety_gate.py",
            "python scripts/run_adapter_audit.py",
            "python scripts/run_workflow_diagnostics.py",
            "python scripts/audit_workflow_status.py",
        ],
        "codex_max_remote_only_rule": True,
        "github_only_source_rule": True,
        "windows_compatible_rule": True,
        "network_default": "disabled",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_to_markdown(snapshot), encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    return 0


def _workflow_rows() -> list[dict[str, str]]:
    path = ROOT / "configs/project/workflow_status.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _to_markdown(snapshot: dict[str, object]) -> str:
    implemented = snapshot["implemented_goals"]
    locked = snapshot["locked_future_goals"]
    lines = [
        "# Current Project Snapshot",
        "",
        f"Governance goal: `{snapshot['governance_goal']}`",
        f"Authoritative remote repository: `{snapshot['authoritative_remote_repository']}`",
        f"Current remote branch: `{snapshot['current_remote_branch']}`",
        f"Latest confirmed remote commit: `{snapshot['latest_confirmed_remote_commit']}`",
        f"Current local branch: `{snapshot['current_local_branch']}`",
        f"Current local commit: `{snapshot['current_local_commit']}`",
        f"Checkpoint branch: `{snapshot['checkpoint_branch']}`",
        f"Checkpoint tag: `{snapshot['checkpoint_tag']}`",
        f"Stable Arch03 commit: `{snapshot['stable_arch03_commit']}`",
        "",
        "The local bundle path is recorded as a user-private backup only. It is",
        "not a Codex Max input, onboarding dependency, or validation dependency.",
        f"User-private local bundle path: `{snapshot['local_bundle_path']}`",
        "",
        f"Latest scientific status: `{snapshot['latest_scientific_status']}`",
        f"Ready factor count: `{snapshot['ready_factor_count']}`",
        f"Refined factor state: {snapshot['refined_factor_state']}",
        f"Regime label state: {snapshot['regime_label_state']}",
        f"Provider catalog state: {snapshot['provider_catalog_state']}",
        f"AKShare catalog state: {snapshot['akshare_catalog_state']}",
        "",
        "## Next Allowed Goals",
        *[f"- `{goal}`" for goal in snapshot["next_allowed_goals"]],
        "",
        "## Implemented Goals",
        *[f"- `{goal}`" for goal in implemented],
        "",
        "## Locked Future Goals",
        *[f"- `{goal}`" for goal in locked],
        "",
        "## Codex Max Rules",
        "- Remote-only rule: `true`",
        "- GitHub-only source rule: `true`",
        "- Windows-compatible rule: `true`",
        "- Provider network default: `disabled`",
        "",
    ]
    return "\n".join(lines)


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else ""


if __name__ == "__main__":
    raise SystemExit(main())
