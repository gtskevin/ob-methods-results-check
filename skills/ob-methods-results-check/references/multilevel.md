# Multilevel and Experience-Sampling Audit

- Map theory, measurement and analysis levels: day/occasion, individual, dyad, leader, team or organization. Record cluster counts, cluster sizes, person N and observation N. One hundred people providing 2,000 diaries are not 2,000 independent participants.
- Inspect dependence treatment in both measurement and structural models. A nonsignificant ICC does not by itself justify ignoring design-based dependence. Distinguish ICC variance partitioning/reliability from within-group agreement and theoretical aggregation justification.
- Match centering and within/between decomposition to the target effect. A group-mean-centered predictor estimates a different relationship from a between-group attribute; do not interpret between-person associations as within-person changes. Inspect contextual terms when needed.
- Review random intercepts/slopes, covariance, cross-level interactions, convergence, singularity and the information available at each level. More random effects are not automatically better; too few clusters can undermine SE and random-effect estimation.
- Inspect resampling and SE procedures against the sampling design and estimand. Ordinary row bootstrap of dependent observations may break clustering; choose a justified cluster/multilevel procedure or other suitable inference, not a universal resampling recipe.
- For ESM inspect timing, person-level compliance, lag construction (including overnight gaps), missing occasions and residual serial dependence. Use [longitudinal.md](longitudinal.md) for temporal models and [measurement-quality.md](measurement-quality.md) for level-specific measurement.
- Cross-level moderation plots must identify levels, actual probe values and compatible coefficients. Consult [mediation-moderation.md](mediation-moderation.md) and recalculation boundaries for random-slope indirect effects.

Methodological anchor: [Aguinis et al., cross-level interactions](https://doi.org/10.1177/0149206313478188).
