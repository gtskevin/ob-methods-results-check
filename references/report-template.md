# Report Template

Write an editable Markdown report as the source of truth. Follow the user's language unless the user requests another language.

Use:

```markdown
# [Paper Title] Methods and Results Audit

**状态：** 待评审

## 1. Overall assessment
## 2. Audit scope and limitations
## 3. P0: Issues that may change core conclusions
## 4. P1: Items requiring review before submission
## 5. P2: Transparency and wording improvements
## 6. Recommended rerun order
## 7. Files to request from collaborators
## 8. Audit boundaries
```

For each P0 or P1 issue, include:

1. Location.
2. Current claim.
3. Evidence or recalculation.
4. Why it matters.
5. Evidence status.
6. Artifact needed next.
7. Repair action.

Keep the chat summary short and link the HTML report.

Save the report under `audit-reports/<paper-slug>/` without overwriting an earlier audit. When Python is available, resolve `$SKILL_DIR` to the absolute directory containing the loaded `SKILL.md` and invoke the bundled renderer with absolute paths:

```bash
python3 "$SKILL_DIR/scripts/render_report.py" "/absolute/path/to/audit-reports/<paper-slug>/report.md"
```

If Python is unavailable, deliver the Markdown-only report and disclose that HTML rendering and deterministic recalculation were unavailable. If PDF page rendering is unavailable, disclose that tables and figures could not be visually verified.
