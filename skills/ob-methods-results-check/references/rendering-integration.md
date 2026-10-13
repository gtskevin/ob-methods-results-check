# Optional external rendering integration

When a user requires Pretty Doc, run that renderer first, then preserve its layout while styling the explicit dashboard table:

```bash
python3 "$SKILL_DIR/scripts/render_report.py" "/absolute/path/report.md" --pretty-doc-html "/absolute/path/report.html" --output "/absolute/path/report.html" --overwrite --open
```

Use this overwrite only for the just-generated HTML in the new report directory, never an earlier audit. The editable Markdown retains the counts and full issue index.

Only use this mode with the just-generated HTML from the same Markdown source and a trusted local renderer/template; it preserves that HTML and is not an HTML sanitizer. When unavailable, use the bundled standalone renderer.
