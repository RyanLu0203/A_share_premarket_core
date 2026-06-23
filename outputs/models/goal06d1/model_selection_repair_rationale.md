# GOAL-06D.1 Model Selection Repair Rationale

Selected repaired score variant: `raw_score_based_alpha_ranking`
Selected target: `excess_fwd_3d_return`
Selection label: `review_only_selected_baseline_weak_but_bounded`

Does any repaired score variant improve stability over GOAL-06D? `bounded_improvement_review_only`
Does any repaired score variant reduce calibration warnings? `partially; calibration remains not reliable for thresholding where marked`
Does any repaired score variant reduce feature sign instability? `partially; unstable features are bounded with monitor/neutralize/research actions`
Does any repaired score variant remain weak? `true`
Is the selected baseline still review-only? `true`
Is GOAL-07A allowed only as design-only preparation? `true`

The repaired baseline is not a production model, recommendation model, trading model, deployed model, or live model.
