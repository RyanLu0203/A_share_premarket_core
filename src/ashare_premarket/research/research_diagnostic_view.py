"""Research-only diagnostic view over committed evidence (GOAL-RESEARCH-DIAGNOSTIC-DASHBOARD-V0).

Read-only. Consumes only already-committed research evidence and renders it for
morning review. It creates no new signal, readiness, recommendation, or position
semantics, writes no actionable output, and touches no governance/workflow state.
It is NOT GOAL-REC-TIERING-01, NOT the locked ``dashboard_daily_report`` product
gate, and does not unlock either. Rendering is produced in-memory (served at
runtime by the ``apps`` entrypoint); no HTML/frontend artifact is committed.
"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

VIEW_ID = "GOAL-RESEARCH-DIAGNOSTIC-DASHBOARD-V0"
DISCLAIMER = (
    "Research diagnostic view only. Read-only over committed evidence. "
    "Not a signal, recommendation, ready classification, or trading interface. "
    "No BUY/SELL/HOLD, no target prices, no positions or weights. "
    "GOAL-REC-TIERING-01 remains locked; ready_factor_count remains 0."
)

# Committed evidence consumed, grouped by review module. Every path is read-only.
INPUTS: dict[str, str] = {
    "factor_diagnostic_overview": "outputs/research/factor_metric_diagnostic_overview.csv",
    "factor_overall_status": "outputs/research/goal_quant_research04_factor_overall_status.csv",
    "regime_conditional_summary": "outputs/research/goal_quant_research04_regime_conditional_evaluation_summary.csv",
    "regime_transition_sensitivity": "outputs/research/goal_quant_research04_regime_transition_sensitivity.csv",
    "quant04_construction_warnings": "outputs/research/goal_quant_research04_construction_warnings.csv",
    "leakage_pit_checks": "outputs/research/goal_quant_research04_leakage_pit_checks.csv",
    "regime02_coverage": "outputs/research/goal_regime_label_research02_refined_regime_coverage_summary.csv",
    "regime02_transitions": "outputs/research/goal_regime_label_research02_refined_regime_transition_summary.csv",
    "regime02_warnings": "outputs/research/goal_regime_label_research02_construction_warnings.csv",
    "data_quality_summary": "outputs/data_expansion/goal_data_expansion_research01/data_quality_summary.csv",
    "provider_health": "outputs/data_expansion/goal_data_expansion_research01/provider_health.csv",
}

MANIFEST_PATH = "outputs/research/research_diagnostic_view_v0_manifest.json"


def load_table(root: Path, key: str) -> tuple[list[str], list[dict[str, str]]]:
    """Deterministic loader for one committed evidence table. Missing file -> empty."""
    rel = INPUTS.get(key, key)
    path = root / rel
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def sort_filter_topn(
    rows: list[dict[str, str]],
    sort_by: str | None = None,
    descending: bool = True,
    status_filter: str | None = None,
    top_n: int | None = None,
) -> list[dict[str, str]]:
    """Presentation-only sort/filter/Top-N. Does not mutate or reclassify rows."""
    result = list(rows)
    if status_filter:
        result = [r for r in result if r.get("overall_factor_status") == status_filter]
    if sort_by and result and sort_by in result[0]:
        def key(row: dict[str, str]) -> tuple[int, float, str]:
            raw = row.get(sort_by, "")
            try:
                return (0, float(raw), "")
            except (TypeError, ValueError):
                return (1, 0.0, str(raw))

        result.sort(key=key, reverse=descending)
    if top_n is not None and top_n >= 0:
        result = result[:top_n]
    return result


def build_view_manifest(root: Path) -> dict[str, object]:
    """Reproducible metadata describing the view, its inputs, and confirmed boundaries."""
    inputs_present = {key: (root / rel).exists() for key, rel in INPUTS.items()}
    return {
        "view_id": VIEW_ID,
        "mode": "research_only_read_only_diagnostic_view",
        "modules": [
            "market_regime_context",
            "factor_diagnostic_overview",
            "warnings_integrity",
            "evidence_provenance",
        ],
        "inputs_consumed": dict(sorted(INPUTS.items())),
        "inputs_present": inputs_present,
        "creates_new_signal_semantics": False,
        "creates_readiness_semantics": False,
        "creates_recommendation_semantics": False,
        "creates_position_semantics": False,
        "writes_actionable_output": False,
        "commits_frontend_artifact": False,
        "modifies_workflow_or_governance_state": False,
        "unlocks_goal_rec_tiering01": False,
        "unlocks_dashboard_daily_report": False,
        "ready_factor_count_expected": 0,
        "disclaimer": DISCLAIMER,
    }


def render_html(
    root: Path,
    sort_by: str = "diagnostic_composite_score",
    status_filter: str | None = None,
    top_n: int | None = None,
) -> str:
    sections = [
        _market_regime_context(root),
        _factor_diagnostic_overview(root, sort_by, status_filter, top_n),
        _warnings_integrity(root),
        _evidence_provenance(root),
    ]
    body = "\n".join(sections)
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(VIEW_ID)}</title>"
        "<style>body{font-family:system-ui,Arial,sans-serif;margin:1.2rem;color:#1a1a1a}"
        "h1{font-size:1.3rem}h2{font-size:1.05rem;margin-top:1.6rem;border-bottom:1px solid #ddd}"
        ".disc{background:#fff8e1;border:1px solid #f0d060;padding:.6rem .8rem;border-radius:6px;font-size:.85rem}"
        "table{border-collapse:collapse;font-size:.8rem;overflow-x:auto;display:block;max-width:100%}"
        "th,td{border:1px solid #ddd;padding:.25rem .45rem;text-align:left;white-space:nowrap}"
        "th{background:#f4f4f4}.muted{color:#666;font-size:.8rem}</style></head><body>"
        f"<h1>{html.escape(VIEW_ID)}</h1>"
        f"<div class=\"disc\">{html.escape(DISCLAIMER)}</div>"
        f"{body}"
        "</body></html>"
    )


def _market_regime_context(root: Path) -> str:
    cov_h, cov = load_table(root, "regime02_coverage")
    tr_h, tr = load_table(root, "regime02_transitions")
    parts = ["<h2>1. Market / Regime Context</h2>"]
    parts.append("<h3 class=\"muted\">Regime coverage (Regime02, committed)</h3>")
    parts.append(_table(cov_h, cov))
    parts.append("<h3 class=\"muted\">Regime transitions (Regime02, committed)</h3>")
    parts.append(_table(tr_h, tr))
    return "\n".join(parts)


def _factor_diagnostic_overview(root: Path, sort_by: str, status_filter: str | None, top_n: int | None) -> str:
    headers, rows = load_table(root, "factor_diagnostic_overview")
    view = sort_filter_topn(rows, sort_by=sort_by, status_filter=status_filter, top_n=top_n)
    caption = (
        f"Showing {len(view)} of {len(rows)} factors"
        + (f", filtered status={html.escape(status_filter)}" if status_filter else "")
        + (f", sorted by {html.escape(sort_by)}" if sort_by else "")
        + (f", Top-{top_n}" if top_n is not None else "")
        + ". Ordering is for exploration only and confers no readiness or recommendation."
    )
    return (
        "<h2>2. Factor Diagnostic Overview</h2>"
        f"<p class=\"muted\">{caption}</p>"
        f"{_table(headers, view)}"
    )


def _warnings_integrity(root: Path) -> str:
    parts = ["<h2>3. Warnings / Integrity</h2>"]
    for label, key in [
        ("PIT / leakage checks", "leakage_pit_checks"),
        ("Quant04 construction / weak-signal warnings", "quant04_construction_warnings"),
        ("Regime02 construction warnings", "regime02_warnings"),
        ("Data-quality summary", "data_quality_summary"),
        ("Provider health", "provider_health"),
    ]:
        h, rows = load_table(root, key)
        parts.append(f"<h3 class=\"muted\">{html.escape(label)}</h3>")
        parts.append(_table(h, rows))
    return "\n".join(parts)


def _evidence_provenance(root: Path) -> str:
    rows = [
        {"module_input": key, "source_file": rel, "present": str((root / rel).exists()).lower()}
        for key, rel in sorted(INPUTS.items())
    ]
    return (
        "<h2>4. Evidence / Provenance</h2>"
        "<p class=\"muted\">All panels above are rendered read-only from these committed files.</p>"
        f"{_table(['module_input', 'source_file', 'present'], rows)}"
        f"<p class=\"disc\">{html.escape(DISCLAIMER)}</p>"
    )


def _table(headers: list[str], rows: list[dict[str, str]]) -> str:
    if not headers:
        return "<p class=\"muted\">(evidence file not present)</p>"
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(row.get(h, '')))}</td>" for h in headers)
        body_rows.append(f"<tr>{cells}</tr>")
    if not body_rows:
        return "<p class=\"muted\">(no rows)</p>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def write_manifest(root: Path) -> Path:
    path = root / MANIFEST_PATH
    path.write_text(json.dumps(build_view_manifest(root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
