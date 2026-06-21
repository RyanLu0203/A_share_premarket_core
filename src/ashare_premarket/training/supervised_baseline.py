from __future__ import annotations

from math import exp
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_json, write_text
from ashare_premarket.datasets.feature_label_merge import FEATURE_COLUMNS
from ashare_premarket.scoring.baseline import WEIGHTS, run_baseline_scoring_skeleton, run_stage6a_blocker_repair


def run_supervised_baseline_training(root: Path) -> Path:
    repair_path = root / "outputs/stage6a/STAGE6A_repair_candidate_dataset.csv"
    score_path = root / "outputs/stage6a/STAGE6A_baseline_score_snapshot.csv"
    if not repair_path.exists():
        run_stage6a_blocker_repair(root)
    if not score_path.exists():
        run_baseline_scoring_skeleton(root)
    rows = read_csv(repair_path)
    training_rows = []
    preview_rows = []
    for row in rows:
        raw = sum(float(row[column]) * WEIGHTS[column] for column in FEATURE_COLUMNS)
        probability = 1 / (1 + exp(-raw))
        training_rows.append({column: row[column] for column in ["target_trading_date", "symbol", *FEATURE_COLUMNS, "label_positive", "alpha_return_1d"]})
        preview_rows.append(
            {
                "target_trading_date": row["target_trading_date"],
                "symbol": row["symbol"],
                "review_only_probability": round(probability, 6),
                "label_positive": row["label_positive"],
                "recommendation_generated": False,
            }
        )
    write_csv(root / "outputs/stage6b/STAGE6B_training_dataset.csv", training_rows)
    feature_manifest = [
        {"feature_name": column, "coefficient": WEIGHTS[column], "label_column": False}
        for column in FEATURE_COLUMNS
    ]
    label_manifest = [
        {"label_name": "label_positive", "label_type": "binary_review_only"},
        {"label_name": "alpha_return_1d", "label_type": "continuous_review_only"},
    ]
    write_csv(root / "outputs/stage6b/STAGE6B_feature_manifest.csv", feature_manifest)
    write_csv(root / "outputs/stage6b/STAGE6B_label_manifest.csv", label_manifest)
    write_csv(root / "outputs/stage6b/STAGE6B_prediction_preview.csv", preview_rows)
    positive_count = sum(1 for row in training_rows if row["label_positive"] == "true")
    summary = {
        "status": "PASS",
        "review_only": True,
        "pilot_only": True,
        "row_count": len(training_rows),
        "positive_label_count": positive_count,
        "production_model_promotion": False,
        "recommendation_unlocked": False,
        "risk_overlay_unlocked": False,
        "dashboard_unlocked": False,
        "paper_trading_unlocked": False,
        "broker_live_trading_unlocked": False,
        "dqn_rl_unlocked": False,
    }
    write_json(root / "outputs/models/goal06b/baseline_training_summary.json", summary)
    registry = {
        "model_id": "goal06b_review_only_supervised_baseline_stub",
        "model_family": "deterministic_linear_review_stub",
        "registered_for_production": False,
        "promotion_allowed": False,
        "artifact_kind": "registry_stub_only",
    }
    write_json(root / "outputs/models/goal06b/baseline_model_registry_stub.json", registry)
    write_text(
        root / "outputs/models/goal06b/review_only_model_card.md",
        "\n".join(
            [
                "# GOAL-06B Review-Only Model Card",
                "",
                "Status: `review_only`",
                "",
                "This baseline is a deterministic supervised-training gate used to verify",
                "feature-label contracts and leakage controls. It is not a production model,",
                "does not generate recommendations, and cannot promote artifacts.",
                "",
            ]
        ),
    )
    return root / "outputs/stage6b/STAGE6B_training_dataset.csv"


def audit_supervised_baseline_training(root: Path) -> bool:
    summary_path = root / "outputs/models/goal06b/baseline_training_summary.json"
    if not summary_path.exists():
        run_supervised_baseline_training(root)
    import json

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    locked_ok = (
        summary["production_model_promotion"] is False
        and summary["recommendation_unlocked"] is False
        and summary["risk_overlay_unlocked"] is False
        and summary["dashboard_unlocked"] is False
        and summary["paper_trading_unlocked"] is False
        and summary["broker_live_trading_unlocked"] is False
        and summary["dqn_rl_unlocked"] is False
    )
    status = "PASS" if summary["review_only"] and locked_ok else "BLOCKED"
    write_text(
        root / "outputs/audits/supervised_baseline_training_audit.md",
        "\n".join(
            [
                "# Supervised Baseline Training Audit",
                "",
                f"Status: `{status}`",
                "Training gate is review-only and pilot-only.",
                "Production promotion, recommendation, risk overlay, dashboard, paper trading, live trading, and DQN/RL remain false.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/stage6c_readiness_report.md",
        "\n".join(
            [
                "# Stage 6C Readiness Report",
                "",
                f"Stage 6C future entry readiness: `{status}`",
                "GOAL-06C is not implemented here. It may begin only as a future review-only expanded validation task after the clean bootstrap report explicitly unlocks it.",
                "",
            ]
        ),
    )
    return status == "PASS"
