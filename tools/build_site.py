#!/usr/bin/env python3
"""Build the static HTML site for the Ask Your Files AI Guide.

Converts every Markdown file in docs/ into a page in site/, plus an
index page with a table of contents. Standard library only: no network,
no frameworks, no third-party packages.

Usage:
    python3 tools/build_site.py            # build site/
    python3 tools/build_site.py --check    # build, then verify links
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

# Reading order for the sidebar/table of contents (docs/index.md first).
TOC_TITLES = {
    "index.md": "Start Here",
    "01-why-pasting-fails.md": "1 · Why Pasting Fails at Scale",
    "02-simple-retrieval.md": "2 · Simple Retrieval: Search, Tagging, Outlines",
    "03-quote-file-rag.md": "3 · Build a Tiny Quote-File RAG",
    "04-folder-packing.md": "4 · The Folder-Packing Approach",
    "05-privacy-rules.md": "5 · Privacy Rules for Personal Files",
    "06-when-to-doubt.md": "6 · When Answers Deserve Doubt",
    "07-first-project.md": "7 · Your First Project",
    "08-checklist.md": "8 · The Session Checklist",
    "09-glossary.md": "9 · Glossary",
}


def _slug(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s]+", "-", s) or "section"


def _inline(text: str) -> str:
    """Inline markdown (code, bold, italic, links) -> HTML.

    Code spans are stashed behind rare sentinel-wrapped markers while
    bold/italic/link transforms run, so asterisks inside code (e.g.
    `2024-02*`) are never mistaken for emphasis, and the digits in normal
    prose are never touched.
    """
    def link_repl(m: re.Match) -> str:
        label, href = m.group(1), m.group(2)
        href = re.sub(r"\.md\b", ".html", href)
        return f'<a href="{html.escape(href, quote=True)}">{label}</a>'

    out = html.escape(text, quote=False)

    stashed: list[str] = []
    ST, EN = "\x00", "\x01"

    def stash(m: re.Match) -> str:
        # Text was already html-escaped above; don't escape it twice.
        stashed.append(f"<code>{m.group(1)}</code>")
        return f"{ST}{len(stashed) - 1}{EN}"

    def unstash(m: re.Match) -> str:
        return stashed[int(m.group(1))]

    out = re.sub(r"`([^`]+)`", stash, out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, out)
    if stashed:
        out = re.sub("\x00([0-9]+)\x01", unstash, out)
    return out


def markdown_to_html(md: str) -> str:
    """Convert a practical subset of Markdown to HTML.

    Supports: ATX headings, fenced code blocks, blockquotes, bullet and
    numbered lists (one nesting level), tables, horizontal rules, and the
    inline constructs handled by _inline(). This purpose-built subset covers
    every construct this manual actually uses.
    """
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    used_slugs: set[str] = set()

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        # Fenced code block
        if line.lstrip().startswith("```"):
            lang = line.lstrip()[3:].strip()
            body: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1  # closing fence
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(
                f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>"
            )
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            text = re.sub(r"\s*#+\s*$", "", text)  # trailing #s
            slug = _slug(text)
            base, n = slug, 2
            while slug in used_slugs:
                slug = f"{base}-{n}"
                n += 1
            used_slugs.add(slug)
            inner = _inline(text)
            out.append(
                f'<h{level} id="{slug}">{inner}</h{level}>'
            )
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*(---+|\*\*\*+)\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # Table (header row contains |, next line is separator)
        if "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|?\s*$", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            ths = "".join(f"<th>{_inline(c)}</th>" for c in header)
            body_rows = []
            for r in rows:
                cells = "".join(f"<td>{_inline(c)}</td>" for c in r)
                body_rows.append(f"<tr>{cells}</tr>")
            out.append(
                "<table><thead><tr>" + ths + "</tr></thead><tbody>"
                + "".join(body_rows) + "</tbody></table>"
            )
            continue

        # Blockquote
        if line.lstrip().startswith(">"):
            quote: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            rendered = markdown_to_html("\n".join(quote))
            out.append(f"<blockquote>{rendered}</blockquote>")
            continue

        # Lists (bullet or numbered, one nesting level). Indented sub-items
        # nest under the previous item; indented non-marker lines continue
        # the most recent item; blank lines end the list.
        list_re = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if list_re:
            ordered = bool(re.match(r"\d+\.", list_re.group(2)))
            tag = "ol" if ordered else "ul"
            i += 1
            top: list[str] = [_inline(list_re.group(3))]
            current_sub: list[str] = []

            def fold_sub() -> None:
                if current_sub:
                    top[-1] = top[-1] + "<" + tag + ">" + "".join(current_sub) + "</" + tag + ">"
                    current_sub.clear()

            while i < len(lines):
                lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not lm:
                    stripped = lines[i].strip()
                    if stripped and lines[i].startswith(("  ",)):
                        # Hard-wrapped continuation of the most recent item.
                        if current_sub:
                            current_sub[-1] = current_sub[-1][:-len("</li>")] + " " + _inline(stripped) + "</li>"
                        else:
                            top[-1] += " " + _inline(stripped)
                        i += 1
                        continue
                    break
                if len(lm.group(1)) >= 2:
                    current_sub.append(f"<li>{_inline(lm.group(3))}</li>")
                    i += 1
                    continue
                fold_sub()
                # A top-level list of the other type ends this list.
                this_ordered = bool(re.match(r"\d+\.", lm.group(2)))
                if this_ordered != ordered:
                    break
                top.append(_inline(lm.group(3)))
                i += 1
            fold_sub()
            lis = "".join(f"<li>{item}</li>" for item in top)
            out.append(f"<{tag}>{lis}</{tag}>")
            continue

        # Paragraph
        para: list[str] = []
        while i < len(lines) and lines[i].strip():
            stop = re.match(r"^(#{1,6}\s|```|\s*>|---+\s*$)", lines[i])
            if stop:
                break
            para.append(lines[i].strip())
            i += 1
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
        else:
            i += 1

    return _merge_adjacent_lists("\n".join(out))


def _merge_adjacent_lists(html_out: str) -> str:
    """Merge two adjacent <ul>/<ol> blocks into one, so a checklist written
    with blank lines between its numbered items still reads 1, 2, 3…."""

    def merge_pair(a: str, b: str, opener: str, closer: str) -> str:
        return a[: -len(closer)] + b[len(opener):]

    blocks = html_out.split("\n")
    merged: list[str] = []
    for block in blocks:
        if merged:
            prev = merged[-1]
            for opener, closer in (("<ul>", "</ul>"), ("<ol>", "</ol>")):
                if prev.startswith(opener) and prev.endswith(closer) \
                        and block.startswith(opener) and block.endswith(closer):
                    merged[-1] = merge_pair(prev, block, opener, closer)
                    break
            else:
                merged.append(block)
        else:
            merged.append(block)
    return "\n".join(merged)


def extract_title(md: str, fallback: str) -> str:
    for line in md.splitlines():
        m = re.match(r"^#\s+(.*)$", line)
        if m:
            return m.group(1).strip()
    return fallback


CSS = """\
:root { --ink:#1c1917; --panel:#faf7f2; --accent:#b45309; --line:#e7e2da; }
* { box-sizing: border-box; }
body { margin:0; font:17px/1.65 Georgia,'Times New Roman',serif; color:var(--ink);
  background:#fdfcfa; }
header.site { background:#171412; color:#f5f1ea; padding:2rem 1rem 1.3rem;
  text-align:center; }
header.site h1 { font-size:1.35rem; margin:0; letter-spacing:.02em; }
header.site p { margin:.35rem 0 0; color:#cfc5b8; font-size:.9rem;
  font-family:system-ui,sans-serif; }
nav.toc { max-width:18rem; float:right; margin:1.5rem 1rem; padding:1rem 1.2rem;
  background:var(--panel); border:1px solid var(--line); border-radius:.5rem;
  font-family:system-ui,sans-serif; font-size:.88rem; position:sticky; top:1rem; }
nav.toc b { display:block; margin-bottom:.4rem; font-size:.8rem; text-transform:uppercase;
  letter-spacing:.08em; color:#8a7f72; }
nav.toc a { display:block; padding:.18rem 0; color:#44403c; text-decoration:none; }
nav.toc a:hover, nav.toc a.current { color:var(--accent); }
main { max-width:46rem; margin:0 auto; padding:2rem 1.3rem 4rem; }
h1,h2,h3 { line-height:1.25; color:#171412; }
h1 { font-size:2rem; margin:0 0 1rem; }
h2 { font-size:1.4rem; margin-top:2.2rem; border-bottom:1px solid var(--line);
  padding-bottom:.25rem; }
h3 { font-size:1.12rem; margin-top:1.6rem; }
code, pre { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.86em; }
code { background:var(--panel); border:1px solid var(--line); border-radius:.25rem;
  padding:.08em .35em; }
pre { background:#171412; color:#f0ead9; padding:1rem 1.1rem; border-radius:.5rem;
  overflow-x:auto; line-height:1.5; }
pre code { background:none; border:none; color:inherit; padding:0; }
blockquote { margin:1.4rem 0; padding:.7rem 1.1rem; background:var(--panel);
  border-left:4px solid var(--accent); border-radius:0 .4rem .4rem 0; }
blockquote p { margin:.4rem 0; }
table { border-collapse:collapse; margin:1.2rem 0; font-size:.93rem; width:100%; }
th,td { border:1px solid var(--line); padding:.45rem .7rem; text-align:left;
  vertical-align:top; }
th { background:var(--panel); }
a { color:var(--accent); }
hr { border:none; border-top:1px solid var(--line); margin:2rem 0; }
footer.site { max-width:46rem; margin:0 auto; padding:1rem 1.3rem 3rem;
  color:#8a7f72; font-size:.85rem; font-family:system-ui,sans-serif; }
footer.site a { color:var(--accent); }
@media (max-width:60rem) { nav.toc { position:static; float:none; max-width:inherit; } }
"""


def page_shell(title: str, body: str, toc_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Ask Your Files AI Guide — a plain-English manual for asking AI questions about your own documents, fully local.">
<title>{html.escape(title)} · Ask Your Files AI Guide</title>
<style>{CSS}</style>
</head>
<body>
<header class="site"><h1>Ask Your Files AI Guide</h1>
<p>a manual by Dylan Asdale · Asdale Dynamics, LLC · fully local, fully yours</p></header>
{toc_html}
<main>
<article>
{body}
</article>
</main>
<footer class="site">
<p>Ask Your Files AI Guide · Copyright (c) 2026 Asdale Dynamics, LLC · MIT licensed ·
built locally from Markdown, no network needed</p>
</footer>
</body>
</html>
"""


def build_toc(current: str) -> str:
    entries = []
    for fname, label in TOC_TITLES.items():
        path = DOCS / fname
        if not path.exists():
            continue
        cls = ' class="current"' if fname == current else ""
        entries.append(f'<a href="{fname[:-3]}.html"{cls}>{html.escape(label)}</a>')
    return '<nav class="toc"><b>Chapters</b>' + "".join(entries) + "</nav>"


def build_site(check: bool = False) -> list[str]:
    SITE.mkdir(exist_ok=True)
    md_files = sorted(DOCS.glob("*.md"))
    if not md_files:
        raise SystemExit(f"No .md files found in {DOCS}")

    written: list[str] = []
    for md_path in md_files:
        md = md_path.read_text(encoding="utf-8")
        rel_name = md_path.name
        title = extract_title(md, TOC_TITLES.get(rel_name, rel_name))
        body = markdown_to_html(md)
        page = page_shell(title, body, build_toc(rel_name))
        out_name = md_path.stem + ".html"
        (SITE / out_name).write_text(page, encoding="utf-8")
        written.append(out_name)

    # Link check (optional) and report.
    if check:
        verify_links()
    return written


def verify_links() -> None:
    """Check that every internal link in every generated page resolves."""
    problems = []
    for page in sorted(SITE.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for m in re.finditer(r'href="([^"#]+)(#[^"]*)?"', text):
            href = m.group(1)
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target = (SITE / href.lstrip("/")).resolve()
            if not target.exists():
                problems.append(f"{page.name}: broken link {href}")
    if problems:
        raise SystemExit("Link check failed:\n  " + "\n  ".join(problems))
    print("Link check passed.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="build, then verify all internal links resolve")
    args = ap.parse_args()
    written = build_site(check=args.check)
    print(f"Built {len(written)} pages -> {SITE}")
    for name in written:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
