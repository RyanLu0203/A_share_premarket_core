# Goal Queue

This queue is advisory governance. It does not itself unlock future work.

1. `GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE`
   is the first Codex Max goal after GOAL-CODEX-OPERATING-SYSTEM-01.
2. `GOAL-DATA-EXPANSION-RESEARCH-01-MARKET-REGIME-DATA-EXPANSION-GATE` may
   proceed only after the Codex Max smoke test passes.
3. `GOAL-QUANT-RESEARCH-04-REGIME-CONDITIONAL-FACTOR-EVALUATION-GATE` may only
   proceed after DataExpansion or explicit user approval.
4. `GOAL-REC-TIERING-01` remains locked until `ready_factor_count > 0` and
   explicit user approval.
5. Dashboard remains locked until explicit user approval.
6. Trading, broker, production, local-lake, factor-mining, and DQN/RL remain
   locked or deleted from active mainline.

Codex Max may not reorder this queue or select the next goal independently.
