# Known Warnings And Non-Blockers

- CNINFO did not cover `002475.SZ` in the inspected source evidence branch.
- Tencent returned no usable rows under bounded variants in the inspected source evidence branch.
- Historical GOAL-05/GOAL-06 docs named by the migration objective were absent at expected source paths and remain classified as `CLASS_D_UNCLEAR_KEEP_DOCUMENTED`.
- The Class D source-evidence gap is documented only; it is not active code and does not block Class A GOAL-06B reproducibility.
- GOAL-06C.5 retains the old contract-demo warning as historical engineering-foundation context; GOAL-06C.7 now provides separate source-backed `engineering_pilot` evidence.
- GOAL-06C.6 provider ingestion is disabled by default and records classified failures on the default AKShare path; explicit CloakBrowser reference probes are separate tag-only diagnostics.
- GOAL-06C.7 provider ladder is disabled from network by default; browser-assisted ingestion requires explicit CLI plus env opt-in and counts only schema-valid finance rows.
- GOAL-06D is `PASS_WITH_WARNINGS`: calibration is weak/non-monotonic for the compared review-only baselines, selected baseline is weak, and provider/source concentration is single-mode `akshare_direct`.
- These warnings do not unlock recommendation, risk overlay, dashboard, paper/live trading, production DB writes, production model promotion, or DQN/RL.
