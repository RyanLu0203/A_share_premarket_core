# Legacy Exclusion Summary

The clean target repository intentionally excludes the historical implementation
tree from the source repository.

Excluded categories:

- old demo runners
- old runtime evidence and handoff packages
- old Step1/Step2/Step3/Step4 temporary validation scripts
- obsolete wrappers
- duplicate configs
- obsolete tests
- DQN/RL code and tests
- dashboard code
- paper trading code
- recommendation and risk overlay code
- raw provider payloads
- DBs, notebooks, caches, and private logs

The concise manifest is:

`outputs/audits/legacy_excluded_from_clean_repo_manifest.csv`

Restore note: recover historical files from the source repository only for a
specific future audit. Do not restore them into active target workflow without a
separate goal and validation gate.
