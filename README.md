# OB Methods Results Audit

**Pre-submission audit for Methods & Results sections in OB, management, HRM, and work-psychology manuscripts.**

A portable agent skill that catches statistical inconsistencies, reporting gaps, and interpretation risks before you submit — powered by LLM judgment for design evaluation and bundled scripts for deterministic recalculation.

<div align="center">

![Agent Skill](https://img.shields.io/badge/type-agent--skill-3560a6?style=flat-square)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white)
![MIT License](https://img.shields.io/badge/license-MIT-059669?style=flat-square)

</div>

---

## What It Checks

| Category | Examples |
|----------|----------|
| **Statistical consistency** | Coefficients, sample sizes, df, test statistics across text, tables, and figures |
| **Mediation & moderation** | a×b indirect effects, interaction probing, conditional effects, IMM |
| **CFA / SEM** | Degrees of freedom, fit indices, factor structure, alternative models |
| **Reporting completeness** | Effect sizes, CIs, direct effects, VIF, scale reliability |
| **Interpretation risks** | Causal claims exceeding design, common-method limitations |
| **Tables & figures** | Significance symbols, coefficient types, notation consistency |

## Install

```bash
# Codex / Claude Code
gh skill install gtskevin/ob-methods-results-audit ob-methods-results-audit --agent codex --scope user
gh skill install gtskevin/ob-methods-results-audit ob-methods-results-audit --agent claude-code --scope user
```

Or symlink manually:

```bash
git clone https://github.com/gtskevin/ob-methods-results-audit.git
ln -s /path/to/ob-methods-results-audit/skills/ob-methods-results-audit ~/.agents/skills/ob-methods-results-audit
```

## Usage

Ask your agent to use `$ob-methods-results-audit` and provide the manuscript:

```
请用 $ob-methods-results-audit 审计这篇论文的 Methods 和 Results 部分。
文件：/path/to/manuscript.pdf
```

The skill adapts audit depth to available artifacts:

- **Manuscript only** → targeted audit with high-risk recalculation
- **+ software output** → cross-checks against reported values
- **+ code & data** → selected reproduction of high-risk results

## Output

Reports are rendered as polished HTML with:

- **Audit summary dashboard** — P0/P1/P2 counts at a glance
- **Finding cards** — severity pills, evidence status badges, scroll animations
- **Actionable vs. design-limitation separation** — fixable issues highlighted; structural limitations collapsed
- **Warm editorial design** — paper-toned palette, responsive layout, dark mode, print styles

```bash
# Render HTML report
python3 "$SKILL_DIR/scripts/render_report.py" /path/to/report.md --open

# Open containing folder (for agents without browser access)
python3 "$SKILL_DIR/scripts/render_report.py" /path/to/report.md --folder
```

The renderer auto-generates the filename from the report title and prints the absolute path for easy access.

## How It Works

```
1. Extract PDF text → identify studies, constructs, hypotheses, analyses
2. Load relevant checklists → targeted to manuscript type
3. Deterministic recalculation (Python) → CFA df, indirect effects, VIF
4. LLM judgment → design evaluation, construct validity, inference risks
5. Evidence ledger → severity-coded findings with artifacts and repair actions
6. HTML rendering → interactive report with dashboard, cards, and navigation
```

**Core principle:** Scripts handle deterministic math. LLM handles judgment calls. Neither replaces the other.

## Optional Dependencies

| Tool | Enables |
|------|---------|
| `python3` | Environment checks, recalculation, HTML rendering |
| `pdftotext` | PDF text extraction |
| `pdftoppm` | Visual verification of tables and figures |

Missing tools don't block the audit — the skill falls back to Markdown-only output and discloses limitations.

## Limits

This is a pre-submission review tool. It does not certify statistical correctness. Manuscript-only audits cannot replace inspection of original software output. When page rendering is unavailable, tables and figures cannot be visually verified.

## License

[MIT](LICENSE.txt)
