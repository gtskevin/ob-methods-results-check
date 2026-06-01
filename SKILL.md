---
name: ob-methods-results-audit
description: Audit organizational behavior, management, HRM, and work-psychology manuscript Methods and Results sections before submission. Use when checking field surveys, scenario experiments, mediation, moderation, moderated mediation, CFA, SEM, multilevel reporting, statistical consistency, tables, figures, causal claims, or when the user wants to catch analysis and reporting risks before further writing or journal submission.
---

# OB Methods Results Audit

Review Methods and Results as a pre-submission audit. Default to Chinese unless the user asks otherwise.

## Core stance

- Prioritize issues that may change core conclusions.
- Treat the manuscript, tables, figures, outputs, scripts, and data as one result chain.
- Use scripts for deterministic recalculation only. Use LLM judgment for design, construct, and inferential evaluation.
- Do not claim that an analysis is correct without the necessary raw output or data.
- Keep high-stakes decisions with the researcher.

## Infer audit depth

Do not ask users to select technical modes unless needed.

| Available artifacts | Audit depth |
|---|---|
| Manuscript only | Check internal consistency, recalculate reported values, and list follow-up artifacts |
| Manuscript plus software output | Add manuscript-output cross-checks |
| Manuscript plus output, code, and data | Reproduce selected high-risk results when feasible |
| User requests a quick screen | Report likely P0 issues and next files only |

## Workflow

1. Inventory artifacts and identify Studies, samples, waves, conditions, constructs, hypotheses, analyses, tables, and figures.
2. For PDFs, extract text and render pages. Inspect tables and figures visually.
3. Load [audit-rubric.md](references/audit-rubric.md) and [report-template.md](references/report-template.md).
4. Load only relevant method references:
   - Field surveys: [survey-design.md](references/survey-design.md)
   - Experiments: [experiment-design.md](references/experiment-design.md)
   - Mediation, moderation, or moderated mediation: [mediation-moderation.md](references/mediation-moderation.md)
   - CFA or SEM: [sem-cfa.md](references/sem-cfa.md)
   - Nested data or aggregation: [multilevel.md](references/multilevel.md)
   - Reporting completeness: [reporting-transparency.md](references/reporting-transparency.md)
5. Recalculate reported quantities when enough values are present. Use:

```bash
python3 scripts/recalculate_reported_stats.py --help
```

6. Build an evidence ledger. For each issue, record location, current claim, evidence, judgment, evidence status, severity, required artifact, and repair action.
7. Produce an editable Markdown source and render HTML with:

```bash
pretty-doc path/to/report.md --open
```

8. Keep the chat response short and link the HTML report.

## Severity and evidence status

Use:

- `P0`: may change a core conclusion.
- `P1`: must be checked before submission.
- `P2`: transparency, reporting, or wording improvement.

Label evidence:

- `可直接确认`: manuscript-internal evidence proves the inconsistency.
- `高度疑似`: strong risk signal; inspect original output.
- `必须复核`: important question requiring data, code, or software output.
- `表述改进`: interpretation or reporting should be tightened.

## Hard rules

1. Inspect tables and figures; do not rely on extracted text alone.
2. Recalculate rather than estimate mentally when a deterministic calculation is possible.
3. Do not replace semantic judgment with regex, keyword matching, or mechanical scores.
4. Do not overstate Harman single-factor tests, time separation, or partial experiments as proving causal mechanisms.
5. Distinguish manuscript-only auditing from raw-data reproduction.
6. When a P0 or P1 issue is found, state what original artifact is needed next.
7. Preserve the editable Markdown report as the source of truth and deliver HTML for reading.

