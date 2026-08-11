from __future__ import annotations

from pathlib import Path
import subprocess

from ashare_premarket.ops.adapter_audit import run_adapter_audit
from ashare_premarket.ops.safety import _iter_scannable_files, run_safety_gate
from ashare_premarket.validation import gates
from ashare_premarket.validation.gates import audit_existing_modules


ROOT = Path(__file__).resolve().parents[1]


def test_module_health_gate() -> None:
    assert audit_existing_modules(ROOT)


def test_safety_gate() -> None:
    assert run_safety_gate(ROOT)


def test_safety_scan_excludes_the_git_ignored_local_archive(tmp_path: Path) -> None:
    source = tmp_path / "src" / "module.py"
    source.parent.mkdir()
    source.write_text("VALUE = 1\n", encoding="utf-8")
    private_log = tmp_path / ".local" / "archive" / "runtime.log"
    private_log.parent.mkdir(parents=True)
    private_log.write_text("local only\n", encoding="utf-8")

    scanned = {
        path.relative_to(tmp_path).as_posix()
        for path in _iter_scannable_files(tmp_path)
    }
    assert "src/module.py" in scanned
    assert ".local/archive/runtime.log" not in scanned


def test_adapter_audit() -> None:
    assert run_adapter_audit(ROOT)


def test_program_validation_profile_uses_repository_local_pytest_state(
    tmp_path: Path,
    monkeypatch,
) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(gates.subprocess, "run", fake_run)

    assert gates.run_program_validation_profile(tmp_path)

    pytest_command = next(
        command for command in commands if command[1:4] == ["-m", "pytest", "tests"]
    )
    assert "-p" in pytest_command
    assert "no:cacheprovider" in pytest_command
    assert "--basetemp=outputs/local/pytest-program-validation" in pytest_command
    assert (tmp_path / "outputs/local").is_dir()
