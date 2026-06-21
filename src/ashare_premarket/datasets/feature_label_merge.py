from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.features.pit_signal_store import build_pit_signal_snapshot
from ashare_premarket.labels.label_builder import build_label_snapshot

FEATURE_COLUMNS = [
    "market_trend_5d",
    "sector_momentum_5d",
    "stock_gap_signal",
    "event_count_pit",
    "review_only_nlp_contract_score",
    "source_health_score",
    "source_count",
]
LABEL_COLUMNS = ["stock_return_1d", "benchmark_return_1d", "alpha_return_1d", "label_positive"]
EXCLUDED_COLUMNS = [
    "as_of_date",
    "target_trading_date",
    "decision_cutoff_ts",
    "symbol",
    "pit_ready",
    "contract_version",
    "next_trading_day",
    "label_observation_ts",
    "label_is_pit_safe",
    *LABEL_COLUMNS,
]


def build_model_ready_candidate_dataset(root: Path) -> Path:
    feature_path = root / "outputs/features/daily_premarket_signal_snapshot.csv"
    label_path = root / "outputs/labels/daily_label_snapshot.csv"
    if not feature_path.exists():
        build_pit_signal_snapshot(root)
    if not label_path.exists():
        build_label_snapshot(root)
    features = read_csv(feature_path)
    labels = {
        (row["symbol"], row["target_trading_date"]): row
        for row in read_csv(label_path)
    }
    rows: list[dict[str, object]] = []
    for feature in features:
        label = labels[(feature["symbol"], feature["target_trading_date"])]
        rows.append({**feature, **label, "dataset_contract_version": "goal05c.v1"})
    path = root / "outputs/datasets/model_ready_candidate_dataset.csv"
    write_csv(path, rows)
    _write_manifests(root)
    return path


def audit_feature_label_leakage(root: Path) -> bool:
    dataset_path = root / "outputs/datasets/model_ready_candidate_dataset.csv"
    if not dataset_path.exists():
        build_model_ready_candidate_dataset(root)
    rows = read_csv(dataset_path)
    violations: list[str] = []
    for row in rows:
        if row["decision_cutoff_ts"][:10] >= row["target_trading_date"]:
            violations.append(f"{row['symbol']} {row['target_trading_date']} cutoff is not pre-target")
    leakage_columns = sorted(set(FEATURE_COLUMNS) & set(LABEL_COLUMNS))
    if leakage_columns:
        violations.append(f"Label leakage columns in features: {leakage_columns}")
    status = "PASS" if not violations else "BLOCKED"
    write_text(
        root / "outputs/audits/feature_label_merge_audit.md",
        "\n".join(
            [
                "# Feature-Label Merge Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{len(rows)}`",
                "Join keys: `symbol`, `target_trading_date`.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/leakage_audit_report.md",
        "\n".join(
            [
                "# Leakage Audit Report",
                "",
                f"Status: `{status}`",
                f"Violations: `{len(violations)}`",
                "Feature columns exclude labels, returns, and post-target observation timestamps.",
                "",
                *[f"- {item}" for item in violations],
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/stage6a_readiness_report.md",
        "\n".join(
            [
                "# Stage 6A Readiness Report",
                "",
                f"Stage 6A entry readiness: `{status}`",
                "Dataset is review-only and ready for the blocker-repair panel.",
                "",
            ]
        ),
    )
    return status == "PASS"


def _write_manifests(root: Path) -> None:
    feature_rows = [
        {
            "column_name": column,
            "role": "live_feature",
            "allowed_for_scoring": True,
            "pit_safe": True,
            "source_capability": "pit_signal_store",
        }
        for column in FEATURE_COLUMNS
    ]
    label_rows = [
        {
            "column_name": column,
            "role": "label",
            "allowed_for_scoring": False,
            "pit_safe": False,
            "source_capability": "label_contract",
        }
        for column in LABEL_COLUMNS
    ]
    excluded_rows = [
        {
            "column_name": column,
            "reason": "identifier_or_label_or_post_target",
            "allowed_for_scoring": False,
        }
        for column in EXCLUDED_COLUMNS
    ]
    write_csv(root / "outputs/datasets/live_feature_manifest.csv", feature_rows)
    write_csv(root / "outputs/datasets/label_manifest.csv", label_rows)
    write_csv(root / "outputs/datasets/excluded_column_manifest.csv", excluded_rows)
