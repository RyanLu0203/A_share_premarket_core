from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_CURRENT = "project-current"
CHECKPOINT_BRANCH = "checkpoint/arch03-stable-310559"
CHECKPOINT_TAG = "checkpoint-arch03-stable-310559"


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    branch = _git(["branch", "--show-current"])
    upstream = _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    local_commit = _git(["rev-parse", "HEAD"])
    remote_commit = _git(["rev-parse", upstream]) if upstream else ""

    if branch == "main":
        warnings.append("current branch is main; Codex Max should use project-current unless explicitly instructed")
    if branch != PROJECT_CURRENT and not branch.startswith("codex-max/"):
        warnings.append(f"current branch is {branch}; expected project-current or codex-max/<goal-id>")
    if branch.startswith("codex-max/") and not _git_ok(["merge-base", "--is-ancestor", f"origin/{PROJECT_CURRENT}", "HEAD"]):
        warnings.append("codex-max branch is not confirmed to include origin/project-current")
    if not upstream:
        failures.append("upstream branch is missing")
    if branch == PROJECT_CURRENT and upstream != f"origin/{PROJECT_CURRENT}":
        failures.append(f"project-current upstream mismatch: {upstream}")
    if _git(["status", "--porcelain"]):
        failures.append("worktree is not clean")
    if not _git_ok(["rev-parse", "--verify", f"origin/{PROJECT_CURRENT}"]):
        warnings.append("origin/project-current is missing")
    if not _git_ok(["rev-parse", "--verify", f"origin/{CHECKPOINT_BRANCH}"]):
        warnings.append("remote checkpoint branch is missing from fetched refs")
    if not _git_ok(["rev-parse", "--verify", f"{CHECKPOINT_TAG}^{{}}"]):
        warnings.append("checkpoint tag is missing")

    print(f"current_branch={branch}")
    print(f"upstream_branch={upstream}")
    print(f"latest_local_commit={local_commit}")
    print(f"latest_remote_commit={remote_commit}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if failures:
        print("Latest branch state check: BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Latest branch state check: PASS")
    return 0


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def _git_ok(args: list[str]) -> bool:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


if __name__ == "__main__":
    raise SystemExit(main())
