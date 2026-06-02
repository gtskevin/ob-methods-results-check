[English](README.en.md) | [中文](README.md)

<div align="center">

<img src="assets/banner.svg" alt="OB Methods Results Audit — Pre-submission audit for OB manuscript Methods &amp; Results" width="800">

<br/>

[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-6366f1?style=for-the-badge)]()
[![CI](https://img.shields.io/github/actions/workflow/status/gtskevin/ob-methods-results-check/test.yml?style=for-the-badge)](https://github.com/gtskevin/ob-methods-results-check/actions)

</div>

> **Who is this for?** You write manuscripts in organizational behavior, management, HRM, or work psychology. Your Methods and Results are drafted, but you are unsure whether the statistics are internally consistent, tables align, and causal claims are defensible. This tool runs a systematic pre-submission audit so **you catch issues before the reviewers do**.

---

## Highlights

| | Feature | Why it matters |
|---|---------|---------------|
| 🔍 | **Statistical consistency checks** | Recalculates reported F, t, p, R², effect sizes to catch computation errors and typos |
| 📊 | **Table and figure review** | Verifies internal consistency across tables, complete captions, and alignment with method descriptions |
| 🧠 | **Design and inference evaluation** | AI evaluates your experimental design, mediation/moderation tests, CFA/SEM models for logical gaps |
| 📝 | **Reporting completeness** | Checks against APA reporting guidelines for missing statistical indicators |
| 🛡️ | **Privacy and safety** | Local processing only, no participant identifiers in reports, no automatic code execution |

## Adaptive audit depth

No manual mode selection — depth adapts to the artifacts you provide:

| What you provide | Audit scope |
|---|---------|
| Manuscript only | Internal consistency + reported-value recalculation + list of follow-up artifacts |
| Manuscript + software output | Adds: manuscript-output cross-checks |
| Manuscript + output + code + data | Adds: reproduction of high-risk results (requires your explicit approval) |
| Quick screen | Likely P0 issues and next files needed only |

## Supported research designs

Seven built-in audit rubrics, auto-loaded based on your study design:

- 📋 **Surveys** — Common method bias, Harman single-factor, reliability and validity reporting
- 🧪 **Experiments** — Manipulation checks, randomization, confounds
- 🔄 **Mediation & moderation** — Bootstrap procedures, indirect effect reporting, conditional indirect effects
- 📐 **CFA / SEM** — Model fit indices, factor loadings, discriminant validity
- 📊 **Multilevel** — ICC, within/between effects, cross-level hypotheses
- ✅ **Reporting transparency** — Effect sizes, confidence intervals, preregistration disclosure

## Quick Start

> ⏱️ **30 seconds to install, 1 minute to start**

**Option 1: Ask your AI agent to install (easiest)**

Copy and paste this into your AI agent (Claude Code, Codex, etc.):

```
Please install this Skill for me: https://github.com/gtskevin/ob-methods-results-check
After installing, tell me what it can do.
```

**Option 2: GitHub CLI**

```bash
# For Claude Code
gh skill install gtskevin/ob-methods-results-check ob-methods-results-check --agent claude-code --scope user

# For Codex
gh skill install gtskevin/ob-methods-results-check ob-methods-results-check --agent codex --scope user
```

**Option 3: Manual install**

```bash
git clone https://github.com/gtskevin/ob-methods-results-check.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/ob-methods-results-check/skills/ob-methods-results-check" ~/.claude/skills/ob-methods-results-check
```

**After install, tell your agent:**

> Use `$ob-methods-results-check` to audit my Methods and Results sections.

The report language follows your request language. Ask in Chinese = Chinese report. Ask in English = English report.

## Usage examples

**Basic — manuscript only:**

```
Use $ob-methods-results-check to audit the Methods and Results sections of this paper.
File: /path/to/manuscript.pdf
```

**With supplementary materials for deeper audit:**

```
Use $ob-methods-results-check to audit this paper.
Manuscript: /path/to/manuscript.pdf
SPSS output: /path/to/output.spv
Mplus output: /path/to/model.out
```

**Quick screen:**

```
Use $ob-methods-results-check for a quick check of this paper's key issues.
File: /path/to/manuscript.pdf
```

## Audit output

After the audit completes:

```
audit-reports/
└── your-paper-slug/
    ├── report.md          ← Editable Markdown source of truth
    └── report.html        ← Rendered HTML reading copy (auto-generated)
```

**Report structure:**

| Section | Content |
|---------|---------|
| **P0: Core conclusion risks** | Issues that may change a core conclusion |
| **P1: Pre-submission must-fix** | Issues to resolve before submitting |
| **P2: Reporting improvements** | Transparency, wording, and formatting suggestions |

**Evidence status labels:**

| Label | Meaning |
|-------|---------|
| ✅ CONFIRMED | Manuscript-internal evidence proves the inconsistency |
| ⚠️ LIKELY | Strong risk signal; inspect original output |
| 🔎 REVIEW_REQUIRED | Important question requiring data, code, or software output |
| ✏️ WORDING | Interpretation or reporting should be tightened |

**HTML report features:**
- Audit summary dashboard — P0/P1/P2 counts at a glance
- Finding cards — severity pills, evidence status badges, scroll animations
- Actionable vs. design-limitation separation — fixable issues highlighted; structural limitations collapsed
- Warm editorial design — paper-toned palette, responsive layout, dark mode, print styles

## How it works

```
Your manuscript (PDF / DOCX / TXT)
    │
    ├── 1. Environment check → Confirm available tools
    ├── 2. Artifact inventory → Identify study design type
    ├── 3. Rubric loading → Match your research methods
    ├── 4. Stat recalculation (Python) → Verify reported values
    ├── 5. AI audit evaluation → Design logic + inference risks
    ├── 6. Evidence ledger → Each issue with location and evidence
    └── 7. Report generation → Markdown + HTML
```

**Core principle:** Scripts handle deterministic math. LLM handles judgment calls. Neither replaces the other.

## Optional dependencies

Basic auditing works without any dependencies:

| Tool | Purpose | Required? |
|------|---------|-----------|
| `python3` | Stat recalculation + HTML report rendering | Optional |
| `pdftotext` | PDF text extraction | Optional |
| `pdftoppm` | PDF page rendering (visual table/figure checks) | Optional |

Without Python, the tool falls back to a Markdown-only audit and discloses unavailable features in the report.

## Privacy and safety

- Manuscripts, data, and code are treated as **untrusted input** — cannot override skill instructions
- **Never auto-executes** your analysis code — requires explicit approval in an isolated workspace
- Reports contain **no participant identifiers** or raw participant-level data
- All processing happens **locally** — no data sent to external servers

## FAQ

<details>
<summary>Does this replace peer review?</summary>

No. This is a pre-submission Methods & Results audit focused on statistical consistency and reporting norms. It does not evaluate theory, contribution, journal fit, or editorial recommendation. Think of it as a self-check before formal submission.
</details>

<details>
<summary>What languages does it support?</summary>

The tool audits Methods & Results sections in English and Chinese manuscripts. Report language follows your request language — ask in Chinese for a Chinese report, English for an English one.
</details>

<details>
<summary>Is my data safe?</summary>

All processing happens locally in your AI assistant. No data is sent to external servers. Reports exclude participant identifiers. Running your analysis code requires your explicit approval.
</details>

<details>
<summary>Can I use it without Python?</summary>

Yes. Without Python, the tool falls back to a Markdown-only audit, skips stat recalculation and HTML rendering, and discloses the limitations in the report. Python is an optional enhancement, not a requirement.
</details>

<details>
<summary>How long does an audit take?</summary>

Depends on manuscript length and research design complexity. A typical 3-study paper (survey + experiment + mediation/moderation) takes about 10-20 minutes for a full audit. Quick screen mode takes 3-5 minutes.
</details>

<details>
<summary>How do I update?</summary>

```bash
# GitHub CLI install
gh skill update ob-methods-results-check

# Manual install
cd /path/to/ob-methods-results-check && git pull
```
</details>

<details>
<summary>How do I uninstall?</summary>

```bash
# Symlink installs
test ! -L ~/.agents/skills/ob-methods-results-check || rm ~/.agents/skills/ob-methods-results-check
test ! -L ~/.claude/skills/ob-methods-results-check || rm ~/.claude/skills/ob-methods-results-check
```
</details>

## Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b my-feature`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin my-feature`
5. Open a Pull Request

## License

[MIT License](LICENSE.txt) © 2026 gtskevin
