#!/usr/bin/env python3
"""
Audit report renderer — redesigned with taste-skill anti-slop principles.
Design read: academic audit report for researchers, trust-first editorial language,
  leaning toward Neutral + single muted accent + generous white space.
Dials: VARIANCE=4, MOTION=2, DENSITY=3 (editorial/trust-first preset)
"""
import argparse
import html
import os
import re
import tempfile
import unicodedata
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
PLACEHOLDER = re.compile(r"\x00MDTOKEN:(\d+)\x00")
MAX_PLACEHOLDER_DEPTH = 8; MAX_QUOTE_DEPTH = 64; MAX_OUTPUT_ATTEMPTS = 100

def _slugify(text):
    text = unicodedata.normalize("NFKD", text)
    slug = re.sub(r'[^\w\s\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff-]', '', text)
    return re.sub(r'[\s]+', '-', slug).strip('-').lower() or "section"

def is_safe_link(href):
    if href.startswith(("http://", "https://", "#")): return True
    lp = href.startswith(("./", "../")) or (href.startswith("/") and not href.startswith("//"))
    return lp and "\\" not in href and not ENCODED_SEPARATOR.search(href)

def restore_placeholders(text, placeholders):
    resolved = []; depths = []
    for rendered in placeholders:
        depth = 0
        def restore_dependency(match, _d=[0]):
            nonlocal depth; idx = int(match.group(1))
            if idx >= len(resolved): return ""
            depth = max(depth, depths[idx] + 1)
            return resolved[idx] if depth <= MAX_PLACEHOLDER_DEPTH else ""
        resolved.append(PLACEHOLDER.sub(restore_dependency, rendered)); depths.append(depth)
    def restore_output(match):
        idx = int(match.group(1))
        return resolved[idx] if idx < len(resolved) and depths[idx] <= MAX_PLACEHOLDER_DEPTH else ""
    return PLACEHOLDER.sub("", PLACEHOLDER.sub(restore_output, text).replace("\x00", "&#0;"))

def render_inline(text):
    escaped = html.escape(text, quote=True).replace("\x00", "&#0;"); ph = []
    def stash(r): ph.append(r); return f"\x00MDTOKEN:{len(ph)-1}\x00"
    escaped = INLINE_CODE.sub(lambda m: stash(f"<code>{m.group(1)}</code>"), escaped)
    def rl(m):
        label, href = m.group(1), html.unescape(m.group(2))
        return stash(f'<a href="{html.escape(href, quote=True)}">{label}</a>') if is_safe_link(href) else m.group(0)
    escaped = LINK.sub(rl, escaped)
    escaped = GLOSSARY.sub(lambda m: stash(f'<span class="glossary">{m.group(1)}<span class="glossary-tip">{m.group(2)}</span></span>'), escaped)
    escaped = BOLD.sub(r"<strong>\1</strong>", escaped)
    return restore_placeholders(escaped, ph)

def split_table_row(line): return [c.strip() for c in line.strip().strip("|").split("|")]
def is_table_separator(line):
    cells = split_table_row(line); return bool(cells) and all(TABLE_SEPARATOR.fullmatch(c) for c in cells)

def render_table(lines, start):
    headers = split_table_row(lines[start]); idx = start + 2; rows = []
    while idx < len(lines) and "|" in lines[idx] and lines[idx].strip():
        rows.append(split_table_row(lines[idx])); idx += 1
    head = "".join(f"<th>{render_inline(c)}</th>" for c in headers)
    body = "".join("<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>', idx

def starts_block(lines, index):
    s = lines[index].strip()
    if not s or s.startswith(("```", "#", ">")) or ORDERED_ITEM.match(lines[index]) or UNORDERED_ITEM.match(lines[index]): return True
    return index+1 < len(lines) and "|" in lines[index] and is_table_separator(lines[index+1])

def render_markdown(md, qd=0):
    lines = md.splitlines(); out = []; i = 0; sc = {}
    while i < len(lines):
        s = lines[i].strip()
        if not s: i += 1; continue
        if s.startswith("```"):
            lang = s[3:].strip(); i += 1; cl = []
            while i < len(lines) and not lines[i].strip().startswith("```"): cl.append(lines[i]); i += 1
            if i < len(lines): i += 1
            cn = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
            out.append(f"<pre><code{cn}>{html.escape(chr(10).join(cl), quote=False)}</code></pre>"); continue
        h = HEADING.match(s)
        if h:
            lv = len(h.group(1)); ht = h.group(2); rt = render_inline(ht)
            if lv in (2,3,4):
                slug = _slugify(re.sub(r'<[^>]+>', '', ht)); sc[slug] = sc.get(slug,0)+1
                if sc[slug]>1: slug = f"{slug}-{sc[slug]}"
                out.append(f'<h{lv} id="{slug}">{rt}</h{lv}>')
            else: out.append(f"<h{lv}>{rt}</h{lv}>")
            i += 1; continue
        if i+1 < len(lines) and "|" in s and is_table_separator(lines[i+1]):
            t, i = render_table(lines, i); out.append(t); continue
        if s.startswith(">"):
            ql = []
            while i < len(lines) and lines[i].strip().startswith(">"): ql.append(lines[i].strip()[1:].lstrip()); i += 1
            if qd >= MAX_QUOTE_DEPTH: out.append(f"<p>{render_inline(' '.join(ql))}</p>")
            else: out.append(f"<blockquote>{render_markdown(chr(10).join(ql), qd+1)}</blockquote>")
            continue
        if ORDERED_ITEM.match(s):
            items = []
            while i < len(lines):
                m = ORDERED_ITEM.match(lines[i])
                if not m: break
                items.append(f"<li>{render_inline(m.group(1))}</li>"); i += 1
            out.append(f"<ol>{''.join(items)}</ol>"); continue
        if UNORDERED_ITEM.match(s):
            items = []
            while i < len(lines):
                m = UNORDERED_ITEM.match(lines[i])
                if not m: break
                items.append(f"<li>{render_inline(m.group(1))}</li>"); i += 1
            out.append(f"<ul>{''.join(items)}</ul>"); continue
        para = [s]; i += 1
        while i < len(lines) and not starts_block(lines, i): para.append(lines[i].strip()); i += 1
        out.append(f"<p>{render_inline(' '.join(para))}</p>")
    return "\n".join(out)

def _build_toc(body):
    entries = []
    for m in re.finditer(r'<h([23])\s+id="([^"]*)"[^>]*>(.*?)</h\1>', body, re.DOTALL):
        lv, aid, txt = int(m.group(1)), m.group(2), re.sub(r'<[^>]+>', '', m.group(3)).strip()
        cls = "toc-h2" if lv == 2 else "toc-h3"
        entries.append(f'<a href="#{aid}" class="{cls}" data-target="{aid}">{txt}</a>')
    if not entries: return ""
    return '<nav class="toc" role="navigation" aria-label="目录"><div class="toc-title">目录</div>' + "\n".join(entries) + "</nav>"

def _extract_status(body):
    m = re.search(r'<p>\s*<strong>\s*状态[：:]\s*</strong>\s*(.*?)\s*</p>', body, re.DOTALL)
    if not m: return body, ""
    txt = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    cls = "status-review"
    for kw, c in [("待评审","status-review"),("已批准","status-approved"),("设计中","status-designing"),("已否决","status-rejected")]:
        if kw in txt: cls = c; break
    badge = f'<span class="status-badge {cls}">{html.escape(txt)}</span>'
    return body[:m.start()] + body[m.end():], badge



def _wrap_design_limitations(body):
    """Wrap '设计层面的局限' section in a collapsed details element."""
    # Find the h2 for design limitations
    pattern = re.compile(
        r'(<h2\s+id="[^"]*(?:设计|局限)[^"]*"[^>]*>.*?</h2>)(.*?)(?=<h2\s|$)',
        re.DOTALL
    )
    def replace_section(m):
        heading = m.group(1)
        content = m.group(2)
        return (
            '<details class="design-limitations">'
            '<summary>设计层面的局限（无法修改，需在论文中说明）</summary>'
            '<div class="limitation-body">'
            + content.strip() +
            '</div></details>'
        )
    return pattern.sub(replace_section, body)

def _postprocess_audit(body):
    """Post-process rendered HTML: add summary dashboard, wrap findings in cards."""
    # Count findings
    p0_ids = set(re.findall(r'id="p0-(\d+)[^"]*"', body))
    p1_ids = set(re.findall(r'id="p1-(\d+)[^"]*"', body))
    p2_ids = set(re.findall(r'id="p2-(\d+)[^"]*"', body))
    p0_count = len(p0_ids)
    p1_count = len(p1_ids)
    p2_count = len(p2_ids)
    if p2_count == 0:
        p2_count = len(set(re.findall(r'(P2[-\u2011]\d+)', body)))

    summary = (
        '<div class="audit-summary">'
        '<div class="summary-card p0"><div class="count">' + str(p0_count) + '</div>'
        '<div class="label">P0 \u5173\u952e\u95ee\u9898</div>'
        '<div class="desc">\u53ef\u80fd\u6539\u53d8\u6838\u5fc3\u7ed3\u8bba</div></div>'
        '<div class="summary-card p1"><div class="count">' + str(p1_count) + '</div>'
        '<div class="label">P1 \u5fc5\u67e5\u9879\u76ee</div>'
        '<div class="desc">\u6295\u7a3f\u524d\u5fc5\u987b\u6838\u67e5</div></div>'
        '<div class="summary-card p2"><div class="count">' + str(p2_count) + '</div>'
        '<div class="label">P2 \u6539\u8fdb\u5efa\u8bae</div>'
        '<div class="desc">\u900f\u660e\u5ea6\u4e0e\u8868\u8ff0\u4f18\u5316</div></div>'
        '</div>'
    )

    def wrap_finding(m):
        h_tag = m.group(1)
        h_attrs = m.group(2)
        h_text = m.group(3)
        rest = m.group(4)
        severity = "p0" if "p0" in h_attrs.lower() else ("p1" if "p1" in h_attrs.lower() else "p2")
        sev_label = severity.upper()
        id_match = re.search(r'(P[02][-\u2011]\d+)', h_text)
        finding_id = id_match.group(1) if id_match else ""
        ev = ""
        if "\u53ef\u76f4\u63a5\u786e\u8ba4" in rest or "CONFIRMED" in rest:
            ev = '<span class="evidence-pill confirmed">\u25cf \u53ef\u76f4\u63a5\u786e\u8ba4</span>'
        elif "\u9ad8\u5ea6\u7591\u4f3c" in rest or "LIKELY" in rest:
            ev = '<span class="evidence-pill likely">\u25cf \u9ad8\u5ea6\u7591\u4f3c</span>'
        elif "\u5fc5\u987c\u590d\u6838" in rest or "REVIEW_REQUIRED" in rest:
            ev = '<span class="evidence-pill review">\u25cf \u5fc5\u987c\u590d\u6838</span>'
        elif "\u8868\u8ff0\u6539\u8fdb" in rest or "WORDING" in rest:
            ev = '<span class="evidence-pill wording">\u25cf \u8868\u8ff0\u6539\u8fdb</span>'
        return (
            '<div class="finding-card">'
            '<div class="finding-card-header">'
            '<span class="severity-pill ' + severity + '">' + sev_label + '</span>'
            '<span class="finding-id">' + finding_id + '</span>'
            + ev +
            '</div>'
            '<div class="finding-card-body">'
            '<h3 ' + h_attrs + '>' + h_text + '</h3>'
            + rest.strip() +
            '</div></div>'
        )

    pattern = re.compile(
        r'<h([34])\s+(id="[^"]*(?:p0|p1|p2)[^"]*"[^>]*)>(.*?)</h\1>(.*?)(?=<h[234]\s|<div class="audit-summary|$)',
        re.DOTALL | re.IGNORECASE
    )
    body = pattern.sub(wrap_finding, body)

    # Insert summary at the beginning of body content
    body = summary + chr(10) + body

    return body

def build_document(body, title):
    safe_title = html.escape(title, quote=True)
    body, status_badge = _extract_status(body)
    body = _postprocess_audit(body)
    body = _wrap_design_limitations(body)
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.DOTALL)
    toc = _build_toc(body)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<style>
/* === AUDIT REPORT — warm editorial design ===
   Inspired by html-anything data-report template.
   Palette: warm paper (#fafaf7) + terracotta accent (#c96442)
   Typography: system stack with Noto Sans SC, tabular numbers
   Shape: 14px radius cards, consistency locked
*/

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  /* Warm paper palette — NOT cold gray */
  --bg: #fafaf7; --bg-card: #ffffff; --bg-muted: #f4f1ec;
  --text: #15140f; --text-secondary: #5a564e; --text-muted: #8a8478;
  --border: #e7e5e0; --border-light: #f0ece5;

  /* Single accent — warm terracotta, saturation ~65% */
  --accent: #c96442; --accent-subtle: #fdf6f3; --accent-hover: #b05538;
  --accent-faint: #faf5f2;

  /* Severity — warm family, desaturated */
  --p0: #9c2a25; --p0-bg: #fdf5f5; --p0-border: #e8c4c4;
  --p1: #9a6b20; --p1-bg: #fdf8ef; --p1-border: #e8d8b4;
  --p2: #2348b8; --p2-bg: #f0f3fa; --p2-border: #c4d0e8;

  /* Evidence */
  --confirmed: #9c2a25; --likely: #b05538; --review: #9a6b20; --wording: #71717a;

  /* Shape — 14px for cards, 6px for inline (consistency locked) */
  --radius: 14px; --radius-sm: 6px;

  /* Shadows — tinted to warm paper */
  --shadow-sm: 0 1px 0 #f0ece5, 0 2px 8px rgba(21,20,15,0.04);
  --shadow-md: 0 4px 12px rgba(21,20,15,0.06), 0 1px 0 #f0ece5;

  /* Content width */
  --content-max: 68ch; --toc-width: 232px;

  /* Typography */
  --font-body: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
    system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "SF Mono", "Fira Code", "JetBrains Mono", ui-monospace, monospace;
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #1a1916; --bg-card: #222120; --bg-muted: #2a2826;
    --text: #e8e4df; --text-secondary: #a09888; --text-muted: #6a6258;
    --border: #3a3632; --border-light: #2e2b28;
    --accent: #e07a56; --accent-subtle: #2a1e18; --accent-hover: #f09070;
    --accent-faint: #241a15;
    --p0: #d98080; --p0-bg: #2a1616; --p0-border: #4a2020;
    --p1: #d4a858; --p1-bg: #2a2210; --p1-border: #4a3818;
    --p2: #7da4e0; --p2-bg: #161e2a; --p2-border: #203050;
    --confirmed: #d98080; --likely: #e09070; --review: #d4a858; --wording: #71717a;
    --shadow-sm: 0 1px 0 rgba(0,0,0,0.2), 0 2px 8px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.35);
  }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }}
  html {{ scroll-behavior: auto !important; }}
}}

html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg); color: var(--text);
  font-family: var(--font-body); font-size: 16px; line-height: 1.8;
  -webkit-font-smoothing: antialiased; padding: 0; margin: 0;
}}

/* === Skip Link === */
.skip-link {{
  position: absolute; top: -100%; left: 16px;
  background: var(--accent); color: #fff;
  padding: 8px 16px; border-radius: var(--radius-sm);
  font-size: 14px; font-weight: 600; z-index: 9999;
  text-decoration: none; transition: top 0.15s;
}}
.skip-link:focus {{ top: 16px; }}

/* === Focus === */
:focus-visible {{
  outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px;
}}
a:focus-visible {{ box-shadow: 0 0 0 3px rgba(201,100,66,0.15); }}

/* === Layout === */
.page-wrapper {{ display: flex; min-height: 100vh; }}

/* === TOC Sidebar === */
.toc {{
  position: sticky; top: 0; align-self: flex-start;
  width: var(--toc-width); min-width: var(--toc-width); height: 100vh;
  overflow-y: auto; padding: 40px 14px 40px 18px;
  background: var(--bg-card); border-right: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 0;
  scrollbar-width: thin;
}}
.toc-title {{
  font-size: 10.5px; font-weight: 700; letter-spacing: 0.18em;
  color: var(--text-muted); text-transform: uppercase;
  padding: 0 10px 14px; border-bottom: 1px solid var(--border-light); margin-bottom: 6px;
}}
.toc a {{
  display: block; padding: 6px 10px; border-radius: var(--radius-sm);
  color: var(--text-secondary); text-decoration: none;
  font-size: 13px; line-height: 1.5; min-height: 34px;
  transition: background 0.15s, color 0.15s;
}}
.toc a:hover {{ background: var(--bg-muted); color: var(--text); }}
.toc a.toc-h2 {{ font-weight: 600; color: var(--text); }}
.toc a.toc-h3 {{ padding-left: 22px; font-weight: 400; position: relative; }}
.toc a.toc-h3::before {{
  content: ''; position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
  width: 3px; height: 3px; border-radius: 50%; background: var(--text-muted);
}}
.toc a.active {{
  background: var(--accent-subtle); color: var(--accent); font-weight: 600;
}}
.toc a.active.toc-h3::before {{ background: var(--accent); }}

/* === Main === */
.main-content {{
  flex: 1; min-width: 0;
  max-width: calc(var(--content-max) + 96px); padding: 48px 48px 120px;
}}

/* === Title Banner === */
.title-banner {{
  margin-bottom: 40px; padding-bottom: 24px;
  border-bottom: 1px solid var(--border);
}}
.title-banner h1 {{
  font-size: 28px; font-weight: 800; line-height: 1.35;
  letter-spacing: -0.025em; color: var(--text); margin: 0 0 12px;
}}
.title-banner .meta {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}

/* === Status Badge === */
.status-badge {{
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 12px; border-radius: 100px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
}}
.status-review {{ background: var(--p1-bg); color: var(--p1); }}
.status-approved {{ background: #f0f8f0; color: #1f7a3a; }}
.status-designing {{ background: var(--p2-bg); color: var(--p2); }}
.status-rejected {{ background: var(--p0-bg); color: var(--p0); }}
@media (prefers-color-scheme: dark) {{
  .status-approved {{ background: #142018; color: #6ab06a; }}
}}

/* === Typography === */
h2 {{
  font-size: 18px; font-weight: 700; margin-top: 48px; margin-bottom: 14px;
  padding-bottom: 10px; border-bottom: 1px solid var(--border-light);
  letter-spacing: -0.01em; scroll-margin-top: 20px; color: var(--text);
}}
h3 {{
  font-size: 15px; font-weight: 650; margin-top: 32px; margin-bottom: 10px;
  color: var(--text); scroll-margin-top: 20px;
}}
h4 {{
  font-size: 11px; font-weight: 700; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--text-muted);
  margin-top: 28px; margin-bottom: 10px;
}}
p {{ margin-bottom: 14px; max-width: var(--content-max); }}
a {{ color: var(--accent); text-decoration: none; transition: color 0.15s; }}
a:hover {{ color: var(--accent-hover); }}
strong {{ font-weight: 650; color: var(--text); }}
.num {{ font-feature-settings: 'tnum' on; letter-spacing: -0.02em; }}

/* === Lists === */
ul, ol {{ margin: 8px 0 16px 0; padding-left: 22px; max-width: var(--content-max); }}
li {{ margin-bottom: 5px; line-height: 1.75; }}
li::marker {{ color: var(--text-muted); }}

/* === Tables — warm editorial, uppercase headers === */
.table-wrap {{
  margin: 20px 0 28px; overflow-x: auto; border-radius: var(--radius);
  border: 1px solid var(--border); box-shadow: var(--shadow-sm);
  -webkit-overflow-scrolling: touch;
}}
table {{ width: 100%; border-collapse: collapse; display: table; font-size: 13.5px; background: var(--bg-card); }}
thead tr {{ background: var(--bg-muted); }}
th {{
  padding: 10px 14px; text-align: left;
  font-size: 10.5px; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--text-muted);
  border-bottom: 1px solid var(--border); white-space: nowrap;
}}
td {{
  padding: 10px 14px; border-bottom: 1px solid var(--border-light);
  vertical-align: top; color: var(--text);
}}
tbody tr:last-child td {{ border-bottom: none; }}
tbody tr {{ transition: background 0.15s; }}
tbody tr:hover {{ background: var(--bg-muted); }}
tbody tr:nth-child(even) {{ background: rgba(244,241,236,0.4); }}
@media (prefers-color-scheme: dark) {{
  tbody tr:nth-child(even) {{ background: rgba(42,40,38,0.4); }}
}}

/* === Blockquotes === */
blockquote {{
  margin: 20px 0; padding: 14px 18px;
  border-left: 2px solid var(--accent);
  background: var(--accent-faint); border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
}}
blockquote p {{ margin-bottom: 6px; }}
blockquote p:last-child {{ margin-bottom: 0; }}

/* === Code === */
code {{
  font-family: var(--font-mono); font-size: 0.875em;
  background: var(--bg-muted); border-radius: 3px;
  padding: 0.1em 0.35em; color: var(--p0);
}}
pre {{
  background: var(--bg-muted); border-radius: var(--radius-sm);
  padding: 16px 18px; overflow-x: auto; margin: 16px 0;
  border: 1px solid var(--border-light);
}}
pre code {{ background: transparent; padding: 0; color: var(--text); font-size: 13px; }}

/* === Glossary === */
.glossary {{
  border-bottom: 1px dotted var(--text-muted); cursor: help;
  position: relative; font-weight: 500;
}}
.glossary-tip {{
  background: var(--text); color: var(--bg-card);
  border-radius: var(--radius-sm); display: none;
  font-size: 13px; font-weight: 400; left: 0;
  max-width: 300px; padding: 10px 14px;
  position: absolute; top: 1.6em; width: max-content;
  z-index: 10; box-shadow: var(--shadow-md); line-height: 1.5;
}}
.glossary:focus-within .glossary-tip, .glossary:hover .glossary-tip {{ display: block; }}

/* === Back-to-Top === */
.back-to-top {{
  position: fixed; bottom: 28px; right: 28px;
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--bg-card); border: 1px solid var(--border);
  box-shadow: var(--shadow-md); color: var(--text-muted);
  font-size: 18px; cursor: pointer; z-index: 100;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transform: translateY(8px);
  transition: opacity 0.2s, transform 0.2s, background 0.15s;
  pointer-events: none;
}}
.back-to-top.visible {{ opacity: 1; transform: translateY(0); pointer-events: auto; }}
.back-to-top:hover {{ background: var(--bg-muted); color: var(--text); }}

/* === Mobile TOC === */
.toc-toggle {{
  display: none; position: fixed; bottom: 28px; left: 28px;
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--accent); border: none;
  box-shadow: var(--shadow-md); color: #fff;
  font-size: 18px; cursor: pointer; z-index: 100;
  align-items: center; justify-content: center;
  transition: background 0.15s;
}}
.toc-toggle:hover {{ background: var(--accent-hover); }}

hr {{ border: none; border-top: 1px solid var(--border); margin: 36px 0; }}

/* === Responsive === */
@media (max-width: 1080px) {{
  .toc {{
    position: fixed; left: -100%; top: 0; width: 280px; height: 100vh;
    z-index: 200; transition: left 0.3s;
  }}
  .toc.open {{ left: 0; box-shadow: 4px 0 20px rgba(21,20,15,0.1); }}
  .toc-toggle {{ display: flex; }}
  .toc-overlay {{ display: none; position: fixed; inset: 0; background: rgba(21,20,15,0.15); z-index: 199; }}
  .toc-overlay.open {{ display: block; }}
  .main-content {{ max-width: 100%; padding: 32px 24px 100px; }}
}}
@media (max-width: 640px) {{
  body {{ font-size: 15px; }}
  .main-content {{ padding: 24px 16px 80px; }}
  h2 {{ font-size: 16px; margin-top: 36px; }}
  h3 {{ font-size: 14px; }}
  .table-wrap {{ font-size: 12.5px; }}
  th, td {{ padding: 7px 10px; }}
  .title-banner h1 {{ font-size: 22px; }}
  .back-to-top, .toc-toggle {{ bottom: 16px; width: 36px; height: 36px; font-size: 16px; }}
  .toc-toggle {{ left: 16px; }} .back-to-top {{ right: 16px; }}
}}

/* === Print === */
@media print {{
  .toc, .toc-toggle, .back-to-top, .skip-link {{ display: none !important; }}
  .main-content {{ max-width: 100%; padding: 0; }}
  body {{ background: white; color: black; font-size: 10.5pt; line-height: 1.6; }}
  .table-wrap {{ box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }}
  h2 {{ page-break-after: avoid; margin-top: 24pt; }}
  .title-banner {{ border-bottom: 1.5pt solid #333; }}
}}


/* === Design Limitations (collapsed, de-emphasized) === */
.design-limitations {{
  background: var(--bg-muted); border: 1px solid var(--border-light);
  border-radius: var(--radius); padding: 0; margin: 32px 0;
  overflow: hidden;
}}
.design-limitations > summary {{
  padding: 14px 20px; cursor: pointer;
  font-size: 14px; font-weight: 600; color: var(--text-secondary);
  list-style: none; display: flex; align-items: center; gap: 8px;
}}
.design-limitations > summary::before {{
  content: ''; display: inline-block; width: 16px; height: 16px;
  background: var(--text-muted); mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'%3E%3Cpath d='M9 18l6-6-6-6'/%3E%3C/svg%3E") center/contain no-repeat;
  transition: transform 0.2s;
}}
.design-limitations[open] > summary::before {{ transform: rotate(90deg); }}
.design-limitations > summary::-webkit-details-marker {{ display: none; }}
.design-limitations .limitation-body {{ padding: 0 20px 20px; }}
.design-limitations .limitation-body h3 {{ font-size: 14px; margin-top: 16px; color: var(--text-secondary); }}
.design-limitations .limitation-body p {{ font-size: 14px; color: var(--text-secondary); }}
.design-limitations .limitation-body strong {{ color: var(--text); }}

/* === Scrollbar === */
.toc::-webkit-scrollbar {{ width: 3px; }}
.toc::-webkit-scrollbar-track {{ background: transparent; }}
.toc::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

/* === Audit Summary Dashboard === */
.audit-summary {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
  margin: 0 0 40px; padding: 0;
}}
.summary-card {{
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px 22px;
  box-shadow: var(--shadow-sm); position: relative; overflow: hidden;
}}
.summary-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}}
.summary-card.p0::before {{ background: var(--p0); }}
.summary-card.p1::before {{ background: var(--p1); }}
.summary-card.p2::before {{ background: var(--p2); }}
.summary-card .count {{
  font-size: 36px; font-weight: 800; letter-spacing: -0.03em;
  line-height: 1; margin-bottom: 6px;
}}
.summary-card.p0 .count {{ color: var(--p0); }}
.summary-card.p1 .count {{ color: var(--p1); }}
.summary-card.p2 .count {{ color: var(--p2); }}
.summary-card .label {{
  font-size: 11px; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--text-muted);
}}
.summary-card .desc {{
  font-size: 12.5px; color: var(--text-secondary); margin-top: 6px; line-height: 1.5;
}}

/* === Finding Cards === */
.finding-card {{
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 0;
  margin: 20px 0 24px; box-shadow: var(--shadow-sm);
  overflow: hidden; opacity: 0; transform: translateY(16px);
  transition: opacity 0.4s ease, transform 0.4s ease;
}}
.finding-card.visible {{ opacity: 1; transform: translateY(0); }}
.finding-card-header {{
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  padding: 14px 20px; border-bottom: 1px solid var(--border-light);
  background: var(--bg-muted);
}}
.finding-card-body {{
  padding: 18px 20px;
}}
.finding-card-body > p:last-child {{ margin-bottom: 0; }}

/* Severity Pill */
.severity-pill {{
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 10px; border-radius: 100px;
  font-size: 11px; font-weight: 700; letter-spacing: 0.06em;
}}
.severity-pill.p0 {{ background: var(--p0-bg); color: var(--p0); }}
.severity-pill.p1 {{ background: var(--p1-bg); color: var(--p1); }}
.severity-pill.p2 {{ background: var(--p2-bg); color: var(--p2); }}

/* Evidence Status Pill */
.evidence-pill {{
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 10px; border-radius: 100px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.03em;
  background: var(--bg-muted); border: 1px solid var(--border-light);
}}
.evidence-pill.confirmed {{ color: var(--confirmed); border-color: var(--confirmed); background: rgba(156,42,37,0.06); }}
.evidence-pill.likely {{ color: var(--likely); border-color: var(--likely); background: rgba(176,85,56,0.06); }}
.evidence-pill.review {{ color: var(--review); border-color: var(--review); background: rgba(154,107,32,0.06); }}
.evidence-pill.wording {{ color: var(--wording); border-color: var(--border); }}

@media (prefers-color-scheme: dark) {{
  .evidence-pill.confirmed {{ background: rgba(217,128,128,0.1); }}
  .evidence-pill.likely {{ background: rgba(224,144,112,0.1); }}
  .evidence-pill.review {{ background: rgba(212,168,88,0.1); }}
}}

/* Finding ID */
.finding-id {{
  font-family: var(--font-mono); font-size: 12px; font-weight: 600;
  color: var(--text-muted); letter-spacing: 0.02em;
}}

/* === Scroll Animations === */
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(20px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.animate-in {{
  opacity: 0; transform: translateY(20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}}
.animate-in.visible {{ opacity: 1; transform: translateY(0); }}
@media (prefers-reduced-motion: reduce) {{
  .animate-in, .finding-card {{ opacity: 1 !important; transform: none !important; transition: none !important; }}
}}

/* === Inline Evidence Highlight === */
.evidence-highlight {{
  display: block; margin: 12px 0; padding: 12px 16px;
  background: var(--bg-muted); border-radius: var(--radius-sm);
  border-left: 3px solid var(--border); font-size: 14px;
  color: var(--text-secondary); line-height: 1.65;
}}
.evidence-highlight strong {{ color: var(--text); }}

/* === Responsive for summary === */
@media (max-width: 640px) {{
  .audit-summary {{ grid-template-columns: 1fr; gap: 10px; }}
  .summary-card .count {{ font-size: 28px; }}
  .finding-card-header {{ padding: 10px 14px; }}
  .finding-card-body {{ padding: 14px; }}
}}
</style>
</head>
<body>
<a class="skip-link" href="#main-content">跳转到正文</a>
<div class="page-wrapper">
{toc}
<div class="toc-overlay" id="toc-overlay"></div>
<main class="main-content" id="main-content" role="main">
<div class="title-banner">
<h1>{safe_title}</h1>
<div class="meta">{status_badge}</div>
</div>
{body}
</main>
</div>
<button class="back-to-top" id="back-to-top" aria-label="返回顶部" title="返回顶部">&#8593;</button>
<button class="toc-toggle" id="toc-toggle" aria-label="打开目录" title="目录">&#9776;</button>
<script>
(function() {{
  var tocLinks = document.querySelectorAll('.toc a[data-target]');
  var headings = [];
  tocLinks.forEach(function(l) {{
    var el = document.getElementById(l.getAttribute('data-target'));
    if (el) headings.push({{ el: el, link: l }});
  }});
  function updateActive() {{
    var y = window.scrollY + 80, cur = null;
    for (var i = 0; i < headings.length; i++) {{ if (headings[i].el.offsetTop <= y) cur = headings[i]; }}
    tocLinks.forEach(function(l) {{ l.classList.remove('active'); }});
    if (cur) cur.link.classList.add('active');
  }}
  var st; window.addEventListener('scroll', function() {{ clearTimeout(st); st = setTimeout(updateActive, 60); }}, {{ passive: true }});
  updateActive();
  var btn = document.getElementById('back-to-top');
  window.addEventListener('scroll', function() {{ btn.classList.toggle('visible', window.scrollY > 400); }}, {{ passive: true }});
  btn.addEventListener('click', function() {{ window.scrollTo({{ top: 0, behavior: 'smooth' }}); }});
  var tocToggle = document.getElementById('toc-toggle'), tocNav = document.querySelector('.toc'), tocOverlay = document.getElementById('toc-overlay');
  function closeToc() {{ tocNav.classList.remove('open'); tocOverlay.classList.remove('open'); }}
  tocToggle.addEventListener('click', function() {{ tocNav.classList.toggle('open'); tocOverlay.classList.toggle('open'); }});
  tocOverlay.addEventListener('click', closeToc);
  tocLinks.forEach(function(l) {{ l.addEventListener('click', closeToc); }});

  // Scroll-triggered fade-in for finding cards and animate-in elements
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
    var observer = new IntersectionObserver(function(entries) {{
      entries.forEach(function(entry) {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }}
      }});
    }}, {{ threshold: 0.1, rootMargin: '0px 0px -40px 0px' }});
    document.querySelectorAll('.finding-card, .animate-in').forEach(function(el) {{
      observer.observe(el);
    }});
  }} else {{
    document.querySelectorAll('.finding-card, .animate-in').forEach(function(el) {{
      el.classList.add('visible');
    }});
  }}
}})();
</script>
</body>
</html>
"""

def choose_output_path(requested, overwrite=False, timestamp=None):
    requested = Path(requested)
    if overwrite: return requested
    if requested.is_symlink(): raise FileExistsError(f"Refusing symlink: {requested}")
    if not os.path.lexists(requested): return requested
    stamp = timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    for v in range(1, MAX_OUTPUT_ATTEMPTS+1):
        sfx = "" if v == 1 else f"-{v}"
        c = requested.with_name(f"{requested.stem}-{stamp}{sfx}{requested.suffix}")
        if not os.path.lexists(c): return c
    raise FileExistsError(f"No path after {MAX_OUTPUT_ATTEMPTS} attempts")

def atomic_replace_text(dest, text):
    fd = None; tp = None
    try:
        fd, tn = tempfile.mkstemp(dir=dest.parent, prefix=f".{dest.name}.", suffix=".tmp", text=True)
        tp = Path(tn)
        with os.fdopen(fd, "w", encoding="utf-8") as f: fd = None; f.write(text)
        os.replace(tp, dest)
    finally:
        if fd is not None: os.close(fd)
        if tp is not None: tp.unlink(missing_ok=True)

def _title_to_slug(title):
    """Generate a filesystem-safe slug from report title for use as filename."""
    # Remove common suffixes
    slug = title
    for suffix in [" - 方法与结果审计报告", "— 方法与结果审计报告", " - 审计报告", "— 审计报告",
                    " - Methods and Results Audit", " - Audit Report"]:
        if slug.endswith(suffix):
            slug = slug[: -len(suffix)]
            break
    # Keep CJK, alphanumeric, hyphens; replace other chars with hyphen
    slug = unicodedata.normalize("NFKC", slug)
    slug = re.sub(r"[^\w一-鿿぀-ゟ゠-ヿ-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "audit-report"


def write_html(source, output=None, overwrite=False, open_browser=False, open_folder=False):
    source = Path(source)
    if not source.is_file(): raise FileNotFoundError(f"Not found: {source}")

    md = source.read_text(encoding="utf-8")
    tm = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    title = tm.group(1) if tm else source.stem

    # Auto-generate filename from title when --output is not specified
    if output:
        requested = Path(output)
    else:
        slug = _title_to_slug(title)
        requested = source.parent / f"{slug}.html"

    requested.parent.mkdir(parents=True, exist_ok=True)
    doc = build_document(render_markdown(md), title)
    if overwrite:
        dest = choose_output_path(requested, overwrite=True); atomic_replace_text(dest, doc)
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        for _ in range(MAX_OUTPUT_ATTEMPTS):
            dest = choose_output_path(requested, overwrite=False, timestamp=ts)
            try:
                with dest.open("x", encoding="utf-8") as f: f.write(doc)
            except FileExistsError: continue
            break
        else: raise FileExistsError(f"No path after {MAX_OUTPUT_ATTEMPTS} attempts")

    resolved = dest.resolve()

    if open_browser:
        try: webbrowser.open(resolved.as_uri())
        except: open_folder = True  # fallback to opening folder
    if open_folder:
        try:
            import subprocess
            subprocess.Popen(["open", str(resolved.parent)])
        except: pass

    return dest

def main():
    p = argparse.ArgumentParser(description="Render audit report as standalone HTML.")
    p.add_argument("source", type=Path); p.add_argument("--output", type=Path)
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--open", action="store_true", dest="open_browser",
                   help="Open the HTML report in the default browser")
    p.add_argument("--folder", action="store_true", dest="open_folder",
                   help="Open the containing folder in Finder")
    a = p.parse_args()
    try:
        d = write_html(a.source, output=a.output, overwrite=a.overwrite,
                       open_browser=a.open_browser, open_folder=a.open_folder)
    except UnicodeDecodeError: p.error(f"Not valid UTF-8: {a.source}")
    except OSError as e: p.error(str(e))
    resolved = d.resolve()
    # Print path for agents that cannot open files directly
    print(f"Report saved: {resolved}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
