"""Tests for tools/build_site.py — the Markdown-to-HTML site builder."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_site  # noqa: E402


class MarkdownConverterTests(unittest.TestCase):
    def call(self, md: str) -> str:
        return build_site.markdown_to_html(md)

    def test_headings(self):
        out = self.call("# Title\n\n## Section A\n\n### sub")
        self.assertIn('<h1 id="title">Title</h1>', out)
        self.assertIn('<h2 id="section-a">Section A</h2>', out)
        self.assertIn('<h3 id="sub">sub</h3>', out)

    def test_duplicate_headings_get_unique_ids(self):
        out = self.call("# Dup\n\n## Dup\n\n## Dup")
        ids = re.findall(r'id="([^"]+)"', out)
        self.assertEqual(len(ids), len(set(ids)))

    def test_paragraph_and_inline(self):
        out = self.call("This is **bold**, this is *italic*, this is `code`.")
        self.assertIn("<strong>bold</strong>", out)
        self.assertIn("<em>italic</em>", out)
        self.assertIn("<code>code</code>", out)

    def test_html_is_escaped(self):
        out = self.call("A <script>alert(1)</script> is escaped.")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_links_rewrite_md_to_html(self):
        out = self.call("See [Chapter 2](02-simple-retrieval.md) next.")
        self.assertIn('href="02-simple-retrieval.html"', out)
        self.assertIn(">Chapter 2</a>", out)

    def test_external_links_untouched(self):
        out = self.call("[Ollama](https://ollama.com) is optional.")
        self.assertIn('href="https://ollama.com"', out)

    def test_fenced_code_block_escapes_and_keeps_lang(self):
        out = self.call("```python\nprint('<b>&rsquo;')\n```")
        self.assertIn('<pre><code class="language-python">', out)
        self.assertIn("&lt;b&gt;", out)
        self.assertNotIn("<b>", out)

    def test_blockquote(self):
        out = self.call("> Bring the page,\n> not the library.")
        self.assertIn("<blockquote>", out)
        self.assertIn("Bring the page,", out)
        self.assertIn("not the library.", out)

    def test_bullet_list(self):
        out = self.call("- one\n- two\n- three")
        self.assertIn("<ul>", out)
        self.assertEqual(out.count("<li>"), 3)
        self.assertIn("<li>two</li>", out)

    def test_numbered_list(self):
        out = self.call("1. alpha\n2. beta")
        self.assertIn("<ol>", out)
        self.assertEqual(out.count("<li>"), 2)

    def test_nested_list_folds_into_parent(self):
        out = self.call("- parent\n  - child\n- next")
        self.assertEqual(out.count("<ul>"), 2)
        self.assertLess(out.index("child"), out.index("next"))

    def test_table(self):
        md = "| a | b |\n| --- | --- |\n| 1 | **2** |\n"
        out = self.call(md)
        self.assertIn("<table><thead><tr><th>a</th><th>b</th>", out)
        self.assertIn("<td><strong>2</strong></td>", out)

    def test_horizontal_rule(self):
        self.assertIn("<hr>", self.call("para\n\n---\n\nmore"))

    def test_checkboxes_render_as_list_items(self):
        out = self.call("- [ ] open item\n- [x] done item")
        self.assertEqual(out.count("<li>"), 2)
        self.assertIn("[ ] open item", out)

    def test_code_spans_with_asterisks_are_not_escaped_twice(self):
        out = self.call("Run `cat *.txt > one.txt` and `2024-02*` now.")
        self.assertIn("<code>cat *.txt &gt; one.txt</code>", out)
        self.assertIn("<code>2024-02*</code>", out)
        self.assertNotIn("&amp;gt;", out)

    def test_bold_containing_italic(self):
        out = self.call("- [ ] **Question spans the *whole* pile?**")
        self.assertIn("<strong>Question spans the <em>whole</em> pile?</strong>", out)
        self.assertNotIn("**", out)

    def test_list_item_continuation_lines(self):
        out = self.call("1. first item text\n   wrapped here\n\n2. second item")
        self.assertIn("first item text wrapped here", out)
        self.assertIn("second item", out)
        self.assertEqual(out.count("</li>"), 2)

    def test_adjacent_numbered_lists_merge_numbering(self):
        out = self.call("1. one\n\n2. two\n\n3. three")
        self.assertEqual(out.count("<ol>"), 1)
        self.assertEqual(out.count("<li>"), 3)

    def test_headings_separate_lists(self):
        out = self.call("1. one\n\n## Heading\n\n1. restart")
        self.assertEqual(out.count("<ol>"), 2)


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.written = build_site.build_site()

    def test_all_doc_pages_built(self):
        doc_pages = {p.stem + ".html" for p in (ROOT / "docs").glob("*.md")}
        self.assertEqual(set(self.written), doc_pages)

    def test_pages_exist_on_disk(self):
        for name in self.written:
            self.assertTrue((build_site.SITE / name).is_file(), name)

    def test_index_page_has_title_and_nav(self):
        page = (build_site.SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn("Ask Your Files AI Guide", page)
        self.assertIn('class="toc"', page)
        self.assertIn("Start Here", page)

    def test_no_local_md_links_survive_in_html(self):
        for name in self.written:
            page = (build_site.SITE / name).read_text(encoding="utf-8")
            for m in re.finditer(r'href="([^"]+\.md)"', page):
                self.fail(f"{name} has unconverted .md link: {m.group(1)}")

    def test_link_check_passes(self):
        # raises SystemExit(Exit) on failure -> test fails by exception
        try:
            build_site.verify_links()
        except SystemExit as e:
            self.fail(f"verify_links failed: {e}")

    def test_pages_escape_raw_html_in_source_md(self):
        # No stray unescaped script tags from source content
        for name in self.written:
            page = (build_site.SITE / name).read_text(encoding="utf-8")
            self.assertNotIn("<script", page.lower())

    def test_credits_in_footer(self):
        page = (build_site.SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", page)


class TocTests(unittest.TestCase):
    def test_every_toc_entry_exists(self):
        for fname in build_site.TOC_TITLES:
            self.assertTrue((ROOT / "docs" / fname).is_file(), fname)


if __name__ == "__main__":
    unittest.main()
