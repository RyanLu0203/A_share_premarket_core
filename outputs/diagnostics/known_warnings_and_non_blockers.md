# Known Warnings And Non-Blockers

- CNINFO did not cover `002475.SZ` in the inspected source evidence branch.
- Tencent returned no usable rows under bounded variants in the inspected source evidence branch.
- Historical GOAL-05/GOAL-06 docs named by the migration objective were absent at expected source paths and remain classified as `CLASS_D_UNCLEAR_KEEP_DOCUMENTED`.
- The Class D source-evidence gap is documented only; it is not active code and does not block Class A GOAL-06B reproducibility.
- GOAL-06C.5 retains the old contract-demo warning as historical engineering-foundation context; GOAL-06C.7 now provides separate source-backed `engineering_pilot` evidence.
- GOAL-06C.6 provider ingestion is disabled by default and records classified failures on the default AKShare path; explicit CloakBrowser reference probes are separate tag-only diagnostics.
- GOAL-06C.7 provider ladder is disabled from network by default; browser-assisted ingestion requires explicit CLI plus env opt-in and counts only schema-valid finance rows.
- GOAL-06D is `PASS_WITH_WARNINGS`: calibration is weak/non-monotonic for the compared review-only baselines, selected baseline is weak, and provider/source concentration is single-mode `akshare_direct`.
- GOAL-06D.1 repairs warning diagnostics but remains review-only: weak baseline, calibration not reliable for thresholding where marked, bounded feature instability, and provider concentration disclosure may remain.
- GOAL-07A is design-only. It carries the GOAL-06D.1 warnings into governance design but does not calculate risk values or generate symbol-level risk rows.
- GOAL-07A.1, GOAL-07B.0, GOAL-08B.0, and GOAL-09.0 are review-only governance gates. GOAL-07B may produce non-actionable risk overlay diagnostics only; GOAL-08A may define names-only recommendation contract designs with zero rows. GOAL-STORAGE-01 is infrastructure-only and does not unlock GOAL-08B by itself. GOAL-08B may produce only non-actionable recommendation diagnostic rows. GOAL-09 may produce only non-actionable position-band diagnostic rows. GOAL-09.1 may classify warnings for future dashboard design-readiness only. GOAL-V1-INTEGRITY-01 may verify artifact-lineage and structure only. Recommendation execution, actual positions, position sizing, dashboards, trading, production, backtests, factor mining, broker, local-lake, and DQN/RL remain locked.
- V2 factor research is `planned_locked`, disabled in V1, and has no active factor mining runner or outputs.
- These warnings do not unlock recommendation, position sizing, dashboard, paper/live trading, production DB writes, production model promotion, factor mining, or DQN/RL.
