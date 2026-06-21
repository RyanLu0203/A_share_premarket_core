from __future__ import annotations

from pathlib import Path

from ashare_premarket.ops.adapter_audit import run_adapter_audit
from ashare_premarket.ops.safety import run_safety_gate
from ashare_premarket.validation.gates import audit_existing_modules


ROOT = Path(__file__).resolve().parents[1]


def test_module_health_gate() -> None:
    assert audit_existing_modules(ROOT)


def test_safety_gate() -> None:
    assert run_safety_gate(ROOT)


def test_adapter_audit() -> None:
    assert run_adapter_audit(ROOT)
