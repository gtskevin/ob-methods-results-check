# Regression and Observed-Score Path Models

Use for OLS/hierarchical regression and choosing observed-score paths versus latent SEM. Request model equations, coding, analysis-specific N, coefficient/SE output and diagnostics relevant to the suspected problem.

1. Identify whether the target concerns observed scores or latent constructs. Explain the modeling choice in terms of measurement error, theory, model complexity and available data; neither SEM nor observed-score analysis is universally required or superior. A software/PROCESS model number is not a specification.
2. Check outcome type, functional form, influential observations, heteroskedasticity, dependence and collinearity. Normality of every predictor is not an OLS assumption. Robust SE address particular variance/dependence problems, not confounding or an incorrect mean model; small cluster counts require special care.
3. Evaluate controls by their theoretical/causal role, timing and coding, not their significance or quantity. Post-treatment variables, mediators or colliders can change the estimand or introduce bias. Compare justified specifications transparently; do not search for the one yielding significance.
4. Identify block order and comparison baseline for hierarchical regression, model-specific N, R-squared versus change in R-squared, b versus beta and coefficient units. Comparisons across models need compatible samples and tests.
5. In path models inspect all equations, direct paths, residual covariances, estimator, missingness and clustering. Inspect identification/convergence and measurement treatment through [sem-cfa.md](sem-cfa.md).
6. A standardized coefficient of .20 usually denotes SD units, not a 20% increase. For binary/count outcomes, consult model-specific guidance: odds ratios are not probability ratios; marginal effects and interactions depend on the link and baseline. Do not judge nonlinear effects solely by an OLS-style interaction interpretation.

For a target journal's preference for latent SEM, read [journal-standards.md](journal-standards.md). Control-variable anchor: [Becker (2005)](https://doi.org/10.1177/1094428105278021).
