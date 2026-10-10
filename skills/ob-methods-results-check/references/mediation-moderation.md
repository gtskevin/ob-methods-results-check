# Mediation, Moderation, and Moderated Mediation Audit

## Specification and indirect effects

- Map a, b, c and c-prime to the actual equations, sample, coefficient scale and model. In standard mediation, the outcome equation includes the antecedent. For multiple mediators inspect their ordering, covariance and joint versus separate estimation.
- Reconstruct a*b only when appropriate; read [recalculation-boundaries.md](recalculation-boundaries.md) for rounding, random slopes and nonlinear-model limitations. Name the CI method accurately (bootstrap, Monte Carlo, etc.); examine resampling units and preservation of dependence.
- A nonsignificant total effect does not automatically invalidate an indirect effect. A nonsignificant direct effect does not establish zero direct effect or “complete mediation.” If comparing mechanisms, test the indirect-effect difference directly.
- Separate statistical indirect effects from causal mediation. Temporal order and randomizing X alone do not identify M→Y; inspect confounding and identification assumptions. Match wording to design rather than announcing that a mechanism is proven.

## Interactions and conditional effects

- Verify coding, constituent lower-order terms, centering purpose and the reference value at which main effects apply. Explain deliberate nonhierarchical restrictions rather than silently imposing them.
- Test the interaction or relevant effect contrast. One slope significant and another nonsignificant does not establish their difference.
- Probe continuous moderators at explicitly defined values within a meaningful observed range; reconcile raw-scale versus centered means and SDs. Binary conditions are conditions, not +/-1 SD. Verify simple slopes, Johnson–Neyman intervals, plots and text against the same fitted model; avoid unsupported extrapolation or arbitrary dichotomization.
- For moderated mediation, identify which paths vary. Test an applicable index or a direct conditional-indirect-effect contrast, not two separate CI significance decisions. Distinguish the index from a high-low difference; nonlinear/multiple-moderator models may require different functions/contrasts. An unsupported component interaction alone is not a complete test of the indirect-effect hypothesis.

Sources: [Gelman & Stern, significance differences](https://sites.stat.columbia.edu/gelman/surveys.course/GelmanStern2006.pdf); [Pirlott & MacKinnon, experimental mediation](https://pmc.ncbi.nlm.nih.gov/articles/PMC4999253/).
