# Report Template

Write an editable Markdown report as the source of truth. Follow the user's language unless the user requests another language. Localize every heading and status label to that language.

Use:

```markdown
# [Localized paper title and audit report title]

**[Localized status label]:** [Localized review-pending status]

## 1. [Localized overall assessment heading]
## 2. [Localized audit scope and limitations heading]
## 3. [Localized P0 issues heading]
## 4. [Localized P1 review items heading]
## 5. [Localized P2 transparency improvements heading]
## 6. [Localized rerun order heading]
## 7. [Localized collaborator file request heading]
## 8. [Localized audit boundaries heading]
```

When a full manuscript was provided, state how it was used in the scope section:

- Core audit evidence: Methods, Results, tables, figures, appendices, output, syntax, or code.
- Selective context: abstract, hypotheses, model figure, construct definitions, discussion, limitations, or implications used only for consistency checks.
- Not audited in depth: theory contribution, literature positioning, writing style, journal fit, and references unless the user requested full peer review.

When a Word/DOCX document was provided, state whether DOCX text/tables were structurally extracted, whether the document was rendered to PDF/pages for visual verification, and which layout-sensitive elements could not be verified.

For each P0 or P1 issue, include:

1. Location.
2. Current claim.
3. Evidence or recalculation.
4. Why it matters.
5. Stable evidence code and localized display label.
6. Artifact needed next.
7. Repair action.

Use one stable evidence code for each issue, paired with a localized display label:

- `CONFIRMED`
- `LIKELY`
- `REVIEW_REQUIRED`
- `WORDING`

If the rendered HTML shows an audit readiness score, interpret it as a visual triage aid only. It should not be described as a manuscript score, quality score, or acceptance-probability estimate.

Keep the chat summary short and link the HTML report when rendered.

Save the report to an absolute `audit-reports/<paper-slug>/` path under the directory containing the manuscript, or under another user-approved workspace directory. Do not write it under the installed Skill directory. Never overwrite an earlier audit.

Before invoking bundled tools, resolve the directory containing the loaded `SKILL.md` to an absolute path. Either substitute that absolute path directly or initialize:

```bash
SKILL_DIR="/absolute/path/to/ob-methods-results-check"
```

When Python is available, invoke the bundled renderer with absolute paths:

```bash
python3 "$SKILL_DIR/scripts/render_report.py" "/absolute/path/to/audit-reports/<paper-slug>/report.md"
```

The HTML renderer must escape untrusted raw HTML. Only activate link targets beginning with `http://`, `https://`, `#`, a single `/`, `./`, or `../`; do not activate `//` remote-host paths. For local paths, do not activate backslashes or encoded separators. Render other link targets as inert text. If safe HTML rendering is unavailable, deliver the Markdown path.

If Python or a bundled helper command fails, preserve the audit, disclose the failure, and continue with manual evidence review where feasible. If Python is unavailable, deliver the Markdown-only report and disclose that HTML rendering and deterministic recalculation were unavailable. If PDF text extraction is unavailable or fails on a document, use built-in PDF reading or request DOCX, TXT, or pasted text. If PDF page rendering is unavailable or fails on a document, disclose that tables and figures could not be visually verified and request screenshots of the relevant pages when visual checks matter.

If HTML rendering or opening fails, preserve the Markdown report and report or link its absolute path while disclosing the fallback.
