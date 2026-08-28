# GOAL-LIQUIDITY-CANDIDATE-SOURCE-ACCEPTANCE-01

Status: `PASS_WITH_WARNINGS` (`implemented_infrastructure_only`).

This gate defines the accepted shape of a future 100-symbol candidate source.
It accepts only an official exchange listing, licensed security master, or an
owner-supplied governed bundle. Every row must provide canonical identity,
listing state, source lineage, and an explicit timezone-aware availability
timestamp no later than the decision cutoff.

Outcome-like fields are rejected at the schema level. Future/forward returns,
factor or alpha values, performance, labels, and targets cannot participate in
universe construction even when blank. Fewer than 100 eligible PIT-safe rows
produces a blocked result and an empty accepted universe.

Current committed evidence remains insufficient: the Provider02B panel exposes
50 symbols but is an evaluation panel, not a security-master source, and does
not provide the complete candidate-source contract. This goal performs no
provider call and accepts no candidate universe.
