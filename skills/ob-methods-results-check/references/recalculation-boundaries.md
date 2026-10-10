# Recalculation boundaries

A numeric mismatch is a lead, not a confirmed error. Before using a helper, match the manuscript version, study, sample, model, coefficient scale and estimator to its assumptions. Record these in the finding. Request the relevant original output when the match cannot be established; continue independent checks.

| Check | Applicability and limits |
|---|---|
| Pooled t | Independent groups, equal variances, sample SDs. Do not compare this result with Welch, paired, adjusted, clustered or mixed-model tests as if they were the same statistic. |
| F and R-squared | Overall ordinary least-squares model with an intercept and unadjusted R-squared. Match n and predictor count. Robust F, change F, pseudo/adjusted R-squared and multilevel tests do not follow this identity. |
| VIF from pairwise r | Valid for a model with exactly two predictors. General VIF uses the R-squared from regressing the focal predictor on ALL remaining predictors. A small pairwise correlation cannot rule out multivariate collinearity. |
| a × b | Fixed linear paths on compatible scales from the same model/sample. Random-slope mediation can require the covariance of a and b; nonlinear models may target a different effect. Do not reconstruct a p-value or bootstrap CI from a product of displayed estimates. |
| First-stage moderated mediation | Uses (a + interaction × W) × b with constant b. Prefer actual reported low/high W values on the fitted model scale. SD mode assumes probes at −SD and +SD around model zero; verify centering before interpreting these as mean ± SD. Percentile probes and uncentered means need actual values. |
| CFA degrees of freedom | Conventional covariance-only simple structure, correlated factors and no extra free parameters. Ordinal estimators, means, equality constraints, cross-loadings and correlated residuals need the actual parameterization. A parameter-count mismatch alone does not prove erroneous CFA. |

For example, an uncentered moderator with mean 3 and SD 1 uses W = 2 and 4 for mean ± SD probes, not −1 and +1. If it was centered at mean 3, the equivalent model-scale probes are −1 and +1. Verify which coefficient parameterization was fitted.

## Rounding

Use full-precision output when available. If only rounded values exist, propagate the plausible rounding intervals before asserting a contradiction. The mediation-product helper optionally accepts `--a-decimals`, `--b-decimals`, `--reported`, and `--reported-decimals` together. It assumes rounding to nearest and checks whether the product interval overlaps the reported-effect interval; closed endpoints deliberately give a conservative compatibility screen. Compatibility does not validate the model; incompatibility still requires the applicability checks above. Truncation, transformed coefficients and unknown precision require separate judgment.

Example: a = .12 and b = .23 rounded to two decimals can be consistent with a reported indirect effect of .03. Their displayed product .0276 is not by itself a reporting error.

## Helper output

The JSON keeps `command`, `inputs` and `result`, and adds `assumptions` and `limitations`. Treat it as conditional arithmetic, not evidence of significance or substantive hypothesis support. Record the exact command and source values so the calculation is reproducible. If assumptions are unresolved, use REVIEW_REQUIRED rather than CONFIRMED.
