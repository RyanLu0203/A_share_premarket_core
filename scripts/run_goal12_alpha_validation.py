from __future__ import annotations

import argparse
import json
import subprocess

from _bootstrap import ROOT
from ashare_premarket.alpha_validation.config import load_goal12_config
from ashare_premarket.alpha_validation.data import load_historical_bundle
from ashare_premarket.alpha_validation.pipeline import run_validation_from_bundle
from ashare_premarket.alpha_validation.store import write_local_validation_run
from ashare_premarket.quant_foundation.features import load_feature_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic research-only GOAL-12 validation")
    parser.add_argument("--run-id", default="goal12-validation-v1")
    args = parser.parse_args()
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    config = load_goal12_config(ROOT)
    bundle = load_historical_bundle(
        ROOT,
        dict(config["data_contract"]),
        code_commit=commit,
    )
    result = run_validation_from_bundle(bundle, load_feature_config(ROOT), config)
    manifest = write_local_validation_run(
        ROOT,
        ROOT / "outputs/local/goal12",
        args.run_id,
        result,
    )
    status_counts: dict[str, int] = {}
    for decision in result["decisions"]:
        status = str(decision["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    print(
        json.dumps(
            {
                "status": result["status"],
                "run_id": args.run_id,
                "result_checksum": result["checksum"],
                "manifest_checksum": manifest["checksum"],
                "feature_row_count": result["data_audit"]["feature_row_count"],
                "label_counts_by_horizon": result["data_audit"]["label_counts_by_horizon"],
                "decision_status_counts": status_counts,
                "production_ready": False,
                "ready_factor_count": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
