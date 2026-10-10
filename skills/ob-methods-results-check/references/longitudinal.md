# Longitudinal Models

Use for lagged regression, CLPM, RI-CLPM, growth models and repeated-wave claims; not simply because recruitment occurred on multiple dates.

- First identify the target: between-person prediction, within-person departure/change, temporal ordering or growth. Choose/check the model against this target, available waves, intervals and assumptions. RI-CLPM is not universally preferable to CLPM; neither automatically identifies causality.
- Inspect time-specific N, matching, attrition, missingness assumptions, lag construction, baseline adjustment, interval rationale and whether measures are comparable over time. Trigger [measurement-quality.md](measurement-quality.md) for relevant invariance questions.
- Conventional CLPM paths are not automatically pure within-person effects. RI-CLPM separates stable between-person components under its model assumptions; inspect identification and whether data support that decomposition.
- For growth models inspect the time scale, trajectory shape, random effects and whether claims concern initial differences, slopes or correlated change. A correlation between growth factors is not a causal mechanism.
- Time-separated X, M and Y alone do not establish temporal mediation or eliminate confounding. Request measurement schedule, equations, syntax/output and relevant prior measures before judging a claimed lagged effect.

Source: [The Within-Between Dispute in Cross-Lagged Panel Research](https://doi.org/10.1037/met0000600). For nested occasions and serial dependence, read [multilevel.md](multilevel.md).
