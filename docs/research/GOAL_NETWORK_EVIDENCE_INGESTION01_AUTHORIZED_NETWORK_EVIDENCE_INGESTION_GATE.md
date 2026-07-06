# GOAL-NETWORK-EVIDENCE-INGESTION-01 Authorized Network Evidence Ingestion Gate

Acquires REAL A-share evidence via the credential-free akshare/sina provider under explicit user authorization
(ASHARE_ALLOW_NETWORK_INGESTION=1), then validates and reports on it fully offline. Acquisition is performed once by
`scripts/acquire_goal_network_evidence_ingestion01.py`; the gate/tests replay the committed checksummed snapshot
offline (no network, deterministic). Never lowers thresholds, forces readiness, unlocks RecTiering, or persists secrets.