# Active Path Replacement Audit

Status: `PASS_WITH_WARNINGS`

| old_path | new_path | artifact_or_module | replacement_status | kept_as_fixture | removed_from_active_validation | notes |
| --- | --- | --- | --- | --- | --- | --- |
| outputs/stage6c/STAGE6C_expanded_validation_dataset.csv | outputs/stage6c/STAGE6C_engineering_expanded_validation_dataset_sample.csv | stage6c_validation_panel | not_replaced_contract_demo_only | true | false | engineering_pilot threshold not met; fixture remains contract-demo review-only validation path |

Replacement rule: upgrade the active path only after PIT, label, Stage 6C engineering, blocked-symbol, leakage, diagnostics, and workflow-status gates all pass at `engineering_pilot` or higher.
