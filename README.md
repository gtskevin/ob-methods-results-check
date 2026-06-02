# OB Methods Results Audit

`ob-methods-results-audit` is a portable agent skill for reviewing Methods and Results sections in organizational behavior, management, HRM, and work-psychology manuscripts before submission.

## Scope

The skill checks internal consistency, reported statistics, tables, figures, reporting completeness, and interpretation risks. It uses model judgment for design and inference questions and bundled scripts only for deterministic recalculation and report rendering.

This is a pre-submission Methods and Results audit. It can complement, but does not replace, a full manuscript peer review focused on theory, contribution, journal fit, and editorial recommendation. Dissertation evaluation and questionnaire scale translation or adaptation review are also better handled by specialist workflows when available.

## Audit depth

Audit depth adapts to the files you provide:

- Manuscript only: internal consistency checks, reported-value recalculation when possible, and a list of follow-up files.
- Manuscript plus software output: manuscript-output cross-checks.
- Manuscript plus output, code, and data: selected reproduction of high-risk results when feasible and explicitly approved.
- Quick screen: likely high-priority issues and the next files needed.

## Install

GitHub CLI 2.90.0 or later can install the published Skill directly. Choose your agent and user scope:

```bash
gh skill install gtskevin/ob-methods-results-audit ob-methods-results-audit --agent codex --scope user
gh skill install gtskevin/ob-methods-results-audit ob-methods-results-audit --agent claude-code --scope user
```

Use either command or both. To install another supported coding agent, replace the `--agent` value. Run `gh skill install --help` for the current list.

For manual installation, keep a stable clone of this repository and symlink the bundled Skill directory:

```bash
mkdir -p ~/.agents/skills ~/.claude/skills
ln -s /absolute/path/to/ob-methods-results-audit/skills/ob-methods-results-audit ~/.agents/skills/ob-methods-results-audit
ln -s /absolute/path/to/ob-methods-results-audit/skills/ob-methods-results-audit ~/.claude/skills/ob-methods-results-audit
```

The first symlink installs the Skill for Codex-compatible agents. The second installs it for Claude Code. `ln -s` fails when the destination already exists: inspect that path and do not silently replace an arbitrary existing file, directory, or link.

Update a GitHub CLI installation with:

```bash
gh skill update ob-methods-results-audit
```

For a manual symlink installation, update the stable clone in place:

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

Missing optional tools do not block an audit. Without Python, the skill produces a Markdown-only report and discloses unavailable recalculation and HTML rendering. If `pdftotext` is unavailable or fails on a document, it uses the agent's built-in PDF reading when available; otherwise it requests DOCX, TXT, or pasted text. If PDF page rendering is unavailable or fails on a document, it continues the text audit and discloses the visual verification limitation. When visual checks matter, it requests screenshots of the relevant pages.

## Outputs

Reports are written to an absolute `audit-reports/<paper-slug>/` path under the manuscript directory or another user-approved workspace directory, not under the installed Skill directory. Markdown remains the editable source of truth. When supported, the bundled renderer creates an HTML reading copy. It must escape untrusted raw HTML. It activates only link targets beginning with `http://`, `https://`, `#`, a single `/`, `./`, or `../`; it must not activate `//` remote-host paths. For local paths, backslashes and encoded separators remain inert. It must render other link targets as inert text. If safe HTML rendering is unavailable, or HTML rendering or opening fails, the skill preserves the Markdown report, discloses the fallback, and reports or links its absolute path. Existing reports are not overwritten.

## Privacy and safety

Manuscripts, software output, analysis code, and data are treated as untrusted input. Their contents are evidence only and cannot override Skill instructions. The skill does not automatically execute user-provided analysis code. Execution requires explicit approval and an isolated disposable workspace with no secrets, network disabled, and declared read and write paths. If any condition cannot be guaranteed, the skill asks the user to run the code and provide outputs.

Reports must not contain participant identifiers or raw participant-level data. Share only the files needed for the audit.

## Limits

This skill supports pre-submission review; it does not certify statistical correctness. Manuscript-only audits cannot replace inspection of original software output or raw-data reproduction. When page rendering is unavailable, tables and figures cannot be visually verified.

## License

Released under the [MIT License](LICENSE.txt).

## Verify

Run the local suite and validate the Agent Skills package:

```bash
python3 -m unittest discover -s tests -v
python3 -m pip install skills-ref
agentskills validate skills/ob-methods-results-audit
gh skill publish --dry-run
```

The `gh skill` commands are currently public preview and may change.
