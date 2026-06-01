# OB Methods Results Audit

`ob-methods-results-audit` is a portable agent skill for reviewing Methods and Results sections in organizational behavior, management, HRM, and work-psychology manuscripts before submission.

## Scope

The skill checks internal consistency, reported statistics, tables, figures, reporting completeness, and interpretation risks. It uses model judgment for design and inference questions and bundled scripts only for deterministic recalculation and report rendering.

## Audit depth

Audit depth adapts to the files you provide:

- Manuscript only: internal consistency checks, reported-value recalculation when possible, and a list of follow-up files.
- Manuscript plus software output: manuscript-output cross-checks.
- Manuscript plus output, code, and data: selected reproduction of high-risk results when feasible and explicitly approved.
- Quick screen: likely high-priority issues and the next files needed.

## Install

Keep a stable clone of this repository, create the agent skill parent directories, then create the symlink for your agent:

```bash
mkdir -p ~/.agents/skills ~/.claude/skills
ln -s /absolute/path/to/ob-methods-results-audit ~/.agents/skills/ob-methods-results-audit
ln -s /absolute/path/to/ob-methods-results-audit ~/.claude/skills/ob-methods-results-audit
```

The first path installs the skill for Codex-compatible agents. The second installs it for Claude Code. Use either or both. `ln -s` fails when the destination already exists: inspect that path and do not silently replace an arbitrary existing file, directory, or link.

Update the stable clone in place so the symlink continues to target the current files:

```bash
cd /absolute/path/to/ob-methods-results-audit
git pull
```

Remove only symlink installations with:

```bash
test ! -L ~/.agents/skills/ob-methods-results-audit || rm ~/.agents/skills/ob-methods-results-audit
test ! -L ~/.claude/skills/ob-methods-results-audit || rm ~/.claude/skills/ob-methods-results-audit
```

## Usage

Ask your agent to use `$ob-methods-results-audit` and provide the manuscript or the relevant Methods and Results files. Add software output, analysis code, or data only when you want a deeper audit.

The skill follows the language of your request unless you ask for a different report language.

## Optional dependencies

- `python3`: enables environment checks, deterministic recalculation, and bundled HTML rendering.
- `pdftotext`: enables PDF text extraction.
- `pdftoppm`: enables rendered PDF page inspection for visual checks of tables and figures.

Missing optional tools do not block an audit. Without Python, the skill produces a Markdown-only report and discloses unavailable recalculation and HTML rendering. Without `pdftotext`, it uses the agent's built-in PDF reading when available; otherwise it requests DOCX, TXT, or pasted text. Without PDF page rendering, it continues the text audit and discloses the visual verification limitation. When visual checks matter, it requests screenshots of the relevant pages.

## Outputs

Reports are written to an absolute `audit-reports/<paper-slug>/` path under the manuscript directory or another user-approved workspace directory, not under the installed Skill directory. Markdown remains the editable source of truth. When supported, the bundled renderer creates an HTML reading copy. It must escape untrusted raw HTML and only make safe links active. If safe HTML rendering is unavailable, or HTML rendering or opening fails, the skill preserves the Markdown report, discloses the fallback, and reports or links its absolute path. Existing reports are not overwritten.

## Privacy and safety

Manuscripts, software output, analysis code, and data are treated as untrusted input. Their contents are evidence only and cannot override Skill instructions. The skill does not automatically execute user-provided analysis code. Execution requires explicit approval and an isolated disposable workspace with no secrets, network disabled when feasible, and declared read and write paths. If those conditions cannot be guaranteed, the skill asks the user to run the code and provide outputs.

Reports must not contain participant identifiers or raw participant-level data. Share only the files needed for the audit.

## Limits

This skill supports pre-submission review; it does not certify statistical correctness. Manuscript-only audits cannot replace inspection of original software output or raw-data reproduction. When page rendering is unavailable, tables and figures cannot be visually verified.

## License

Released under the [MIT License](LICENSE.txt).
