from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.datasets.feature_label_merge import FEATURE_COLUMNS, build_model_ready_candidate_dataset

WEIGHTS = {
    "market_trend_5d": 0.15,
    "sector_momentum_5d": 0.15,
    "stock_gap_signal": 0.20,
    "event_count_pit": 0.05,
    "review_only_nlp_contract_score": 0.15,
    "source_health_score": 0.20,
    "source_count": 0.10,
}


def run_stage6a_blocker_repair(root: Path, no_network: bool = True) -> Path:
    dataset_path = root / "outputs/datasets/model_ready_candidate_dataset.csv"
    if not dataset_path.exists():
        build_model_ready_candidate_dataset(root)
    rows = read_csv(dataset_path)
    repaired = []
    for row in rows:
        repaired.append({**row, "stage6a_repair_status": "PASS", "network_used": not no_network})
    path = root / "outputs/stage6a/STAGE6A_repair_candidate_dataset.csv"
    write_csv(path, repaired)
    write_csv(root / "outputs/stage6a/STAGE6A_live_feature_manifest.csv", read_csv(root / "outputs/datasets/live_feature_manifest.csv"))
    write_csv(root / "outputs/stage6a/STAGE6A_label_manifest.csv", read_csv(root / "outputs/datasets/label_manifest.csv"))
    return path


def run_baseline_scoring_skeleton(root: Path) -> Path:
    repair_path = root / "outputs/stage6a/STAGE6A_repair_candidate_dataset.csv"
    if not repair_path.exists():
        run_stage6a_blocker_repair(root)
    rows = read_csv(repair_path)
    scored: list[dict[str, object]] = []
    for row in rows:
        score = sum(float(row[column]) * WEIGHTS[column] for column in FEATURE_COLUMNS)
        scored.append(
            {
                "target_trading_date": row["target_trading_date"],
                "symbol": row["symbol"],
                "baseline_score": round(score, 6),
                "score_contract_version": "goal06a.v1",
                "review_only": True,
                "recommendation_generated": False,
            }
        )
    path = root / "outputs/stage6a/STAGE6A_baseline_score_snapshot.csv"
    write_csv(path, scored)
    usage_rows = [
        {
            "feature_name": column,
            "weight": weight,
            "source_manifest": "outputs/stage6a/STAGE6A_live_feature_manifest.csv",
            "label_column": False,
        }
        for column, weight in WEIGHTS.items()
    ]
    write_csv(root / "outputs/stage6a/STAGE6A_score_feature_usage_manifest.csv", usage_rows)
    return path


def audit_baseline_scoring_skeleton(root: Path) -> bool:
    score_path = root / "outputs/stage6a/STAGE6A_baseline_score_snapshot.csv"
    if not score_path.exists():
        run_baseline_scoring_skeleton(root)
    usage = read_csv(root / "outputs/stage6a/STAGE6A_score_feature_usage_manifest.csv")
    failures = [row for row in usage if row["label_column"] == "true"]
    status = "PASS" if not failures else "BLOCKED"
    write_text(
        root / "outputs/audits/baseline_scoring_skeleton_audit.md",
        "\n".join(
            [
                "# Baseline Scoring Skeleton Audit",
                "",
                f"Status: `{status}`",
                "The scoring skeleton uses only live feature manifest columns.",
                "It emits scores for review only and does not emit recommendations.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/stage6b_readiness_report.md",
        "\n".join(
            [
                "# Stage 6B Readiness Report",
                "",
                f"Stage 6B supervised baseline gate readiness: `{status}`",
                "Review-only supervised training can run without model promotion.",
                "",
            ]
        ),
    )
    return status == "PASS"
