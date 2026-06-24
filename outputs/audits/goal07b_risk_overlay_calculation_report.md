# GOAL-07B Risk Overlay Calculation Prototype

GOAL-07B Risk Overlay Calculation Prototype: PASS_WITH_WARNINGS
GOAL-07B mode: review_only
Risk overlay diagnostic rows generated: `100`
Output grain: `trade_date + symbol`
Risk severity levels used: `HIGH`
No recommendation output was generated
No position output was generated
No dashboard output was generated
No paper/live trading output was generated
No production output was generated
No backtest output was generated
No factor-mining output was generated
No DQN/RL output was generated
Allowed next action: prepare GOAL-08A recommendation contract design gate, or fix GOAL-07B warnings

## Evidence Inputs
- `outputs/samples/stage6c_source_backed_engineering_panel_sample.csv`
- `outputs/stage6c/STAGE6C_source_backed_engineering_panel_coverage_summary.csv`
- `outputs/audits/source_backed_bundle_manifest_summary.json`
- `outputs/models/goal06d1/model_comparison_repair_summary.csv`
- `outputs/models/goal06d1/provider_source_concentration_summary.csv`
- `outputs/models/goal06d1/calibration_repair_summary.csv`
- `outputs/models/goal06d1/feature_sign_stability_repair.csv`
- `outputs/models/goal06d1/target_horizon_comparison.csv`
- `outputs/audits/goal07a1_warning_classification.csv`
- `outputs/audits/goal07b0_unlock_gate_manifest.json`
- `configs/risk/goal07a_allowed_input_contract.yaml`
- `configs/risk/goal07a_risk_rule_catalog.yaml`
- `configs/risk/goal07a_risk_state_machine.yaml`
- `configs/risk/goal07a_upstream_warning_mapping.yaml`

## Warnings Remaining
- `calibration_not_reliable_for_thresholding`
- `feature_sign_instability_bounded`
- `provider_source_concentration_disclosed`
- `selected_score_variant_weak_rank_signal`
- `single_provider_mode_akshare_direct`
- `target_horizon_calibration_warning`
- `weak_target_horizon_rank_signal`

## Failures
