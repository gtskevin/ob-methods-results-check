#!/usr/bin/env python3
import argparse
import html
import os
import re
import webbrowser
from datetime import datetime
from pathlib import Path


TABLE_SEPARATOR = re.compile(r":?-{3,}:?")
ORDERED_ITEM = re.compile(r"^\s*\d+\.\s+(.+)$")
UNORDERED_ITEM = re.compile(r"^\s*[-*]\s+(.+)$")
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\n]*)\)")
GLOSSARY = re.compile(r"\{\{([^|{}\n]+)\|([^{}\n]+)\}\}")
INLINE_CODE = re.compile(r"`([^`\n]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ENCODED_SEPARATOR = re.compile(r"%(?:2f|5c)", flags=re.IGNORECASE)
MAX_QUOTE_DEPTH = 64


def is_safe_link(href):
    if "\\" in href or ENCODED_SEPARATOR.search(href):
        return False
    return (
        href.startswith(("http://", "https://", "#", "./", "../"))
        or (href.startswith("/") and not href.startswith("//"))
    )


def render_inline(text):
    escaped = html.escape(text, quote=True)
    placeholders = {}
    prefix = "\x00MDTOKEN"
    while prefix in escaped:
        prefix += "_"

    def stash(rendered):
        token = f"{prefix}{len(placeholders)}\x00"
        placeholders[token] = rendered
        return token

    escaped = INLINE_CODE.sub(
        lambda match: stash(f"<code>{match.group(1)}</code>"),
        escaped,
    )

    def render_link(match):
        label = match.group(1)
        href = html.unescape(match.group(2))
        if not is_safe_link(href):
            return match.group(0)
        return stash(f'<a href="{html.escape(href, quote=True)}">{label}</a>')

    escaped = LINK.sub(render_link, escaped)
    escaped = GLOSSARY.sub(
        lambda match: stash(
            f'<span class="glossary">{match.group(1)}'
            f'<span class="glossary-tip">{match.group(2)}</span></span>'
        ),
        escaped,
    )
    escaped = BOLD.sub(r"<strong>\1</strong>", escaped)
    token_pattern = re.compile(rf"{re.escape(prefix)}\d+\x00")
    return token_pattern.sub(lambda match: placeholders[match.group(0)], escaped)


def split_table_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line):
    cells = split_table_row(line)
    return bool(cells) and all(TABLE_SEPARATOR.fullmatch(cell) for cell in cells)


def render_table(lines, start):
    headers = split_table_row(lines[start])
    index = start + 2
    rows = []
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        rows.append(split_table_row(lines[index]))
        index += 1

    head = "".join(f"<th>{render_inline(cell)}</th>" for cell in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>", index


def starts_block(lines, index):
    line = lines[index]
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith(("```", "#", ">")):
        return True
    if ORDERED_ITEM.match(line) or UNORDERED_ITEM.match(line):
        return True
    return index + 1 < len(lines) and "|" in line and is_table_separator(lines[index + 1])


def render_markdown(markdown_text, quote_depth=0):
    lines = markdown_text.splitlines()
    output = []
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            index += 1
            code_lines = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            class_name = (
                f' class="language-{html.escape(language, quote=True)}"'
                if language
                else ""
            )
            code = html.escape("\n".join(code_lines), quote=False)
            output.append(f"<pre><code{class_name}>{code}</code></pre>")
            continue

        heading = HEADING.match(stripped)
        if heading:
            level = len(heading.group(1))
            output.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            index += 1
            continue

        if index + 1 < len(lines) and "|" in line and is_table_separator(lines[index + 1]):
            table, index = render_table(lines, index)
            output.append(table)
            continue

        if stripped.startswith(">"):
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip()[1:].lstrip())
                index += 1
            if quote_depth >= MAX_QUOTE_DEPTH:
                output.append(f"<p>{render_inline(' '.join(quote_lines))}</p>")
            else:
                quote = render_markdown("\n".join(quote_lines), quote_depth + 1)
                output.append(f"<blockquote>{quote}</blockquote>")
            continue

        if ORDERED_ITEM.match(line):
            items = []
            while index < len(lines):
                item = ORDERED_ITEM.match(lines[index])
                if not item:
                    break
                items.append(f"<li>{render_inline(item.group(1))}</li>")
                index += 1
            output.append(f"<ol>{''.join(items)}</ol>")
            continue

        if UNORDERED_ITEM.match(line):
            items = []
            while index < len(lines):
                item = UNORDERED_ITEM.match(lines[index])
                if not item:
                    break
                items.append(f"<li>{render_inline(item.group(1))}</li>")
                index += 1
            output.append(f"<ul>{''.join(items)}</ul>")
            continue

        paragraph = [stripped]
        index += 1
        while index < len(lines) and not starts_block(lines, index):
            paragraph.append(lines[index].strip())
            index += 1
        output.append(f"<p>{render_inline(' '.join(paragraph))}</p>")

    return "\n".join(output)


def build_document(body, title):
    safe_title = html.escape(title, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<style>
:root {{ color-scheme: light; }}
body {{ color: #202124; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.65; margin: 0 auto; max-width: 980px; padding: 40px 24px 80px; }}
h1, h2, h3, h4, h5, h6 {{ color: #111827; line-height: 1.25; margin-top: 1.5em; }}
a {{ color: #0969da; }}
table {{ border-collapse: collapse; display: block; margin: 1em 0; max-width: 100%; overflow-x: auto; width: max-content; }}
th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; vertical-align: top; }}
th {{ background: #f6f8fa; }}
blockquote {{ border-left: 4px solid #9ca3af; color: #4b5563; margin-left: 0; padding-left: 16px; }}
code {{ background: #f3f4f6; border-radius: 4px; padding: 0.15em 0.3em; }}
pre {{ background: #f6f8fa; border-radius: 6px; overflow-x: auto; padding: 16px; }}
pre code {{ background: transparent; padding: 0; }}
.glossary {{ border-bottom: 1px dotted #6b7280; cursor: help; position: relative; }}
.glossary-tip {{ background: #111827; border-radius: 4px; color: white; display: none; font-size: 0.85em; left: 0; max-width: 360px; padding: 8px; position: absolute; top: 1.5em; width: max-content; z-index: 2; }}
.glossary:hover .glossary-tip {{ display: block; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def choose_output_path(requested, overwrite=False, timestamp=None):
    requested = Path(requested)
    if overwrite:
        return requested
    if requested.is_symlink():
        raise FileExistsError(
            f"Refusing to write through symlink without --overwrite: {requested}"
        )
    if not os.path.lexists(requested):
        return requested

    stamp = timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = requested.with_name(f"{requested.stem}-{stamp}{requested.suffix}")
    version = 2
    while os.path.lexists(candidate):
        candidate = requested.with_name(
            f"{requested.stem}-{stamp}-{version}{requested.suffix}"
        )
        version += 1
    return candidate


def write_html(source, output=None, overwrite=False, open_browser=False):
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(f"Markdown source not found: {source}")

    requested = Path(output) if output else source.with_suffix(".html")
    requested.parent.mkdir(parents=True, exist_ok=True)
    markdown_text = source.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", markdown_text, flags=re.MULTILINE)
    title = title_match.group(1) if title_match else source.stem
    document = build_document(render_markdown(markdown_text), title)
    if overwrite:
        destination = choose_output_path(requested, overwrite=True)
        destination.write_text(document, encoding="utf-8")
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        while True:
            destination = choose_output_path(
                requested,
                overwrite=False,
                timestamp=timestamp,
            )
            try:
                with destination.open("x", encoding="utf-8") as output_file:
                    output_file.write(document)
            except FileExistsError:
                continue
            break
    if open_browser:
        try:
            webbrowser.open(destination.resolve().as_uri())
        except Exception:
            pass
    return destination


def main():
    parser = argparse.ArgumentParser(
        description="Render an audit Markdown report as standalone HTML."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--open", action="store_true", dest="open_browser")
    args = parser.parse_args()
    try:
        destination = write_html(
            args.source,
            output=args.output,
            overwrite=args.overwrite,
            open_browser=args.open_browser,
        )
    except UnicodeDecodeError:
        parser.error(f"Markdown source is not valid UTF-8: {args.source}")
    except OSError as exc:
        parser.error(str(exc))
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
