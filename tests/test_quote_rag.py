"""Tests for tools/quote_rag.py — the tiny local quote-file RAG.

These tests run fully offline: the Ollama-backed code paths are exercised only
through the "unreachable server" fallback, which is how real users without
Ollama experience the tool.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import quote_rag  # noqa: E402


class TokenizerTests(unittest.TestCase):
    def test_lowercases_and_stops_stopwords(self):
        toks = quote_rag.tokenize("The Claim was DENIED under code CO-97")
        self.assertIn("denied", toks)
        self.assertIn("co", toks)
        self.assertIn("97", toks)
        self.assertNotIn("the", toks)
        self.assertNotIn("was", toks)

    def test_single_letters_dropped(self):
        self.assertEqual(quote_rag.tokenize("a b cd"), ["cd"])


class ChunkingTests(unittest.TestCase):
    def test_split_on_blank_lines(self):
        text = "First paragraph.\n\nSecond paragraph."
        quotes = quote_rag.split_into_quotes(text)
        self.assertEqual(len(quotes), 2)
        self.assertEqual(quotes[0]["text"], "First paragraph.")

    def test_heading_recorded_and_consumed(self):
        text = "## Deductible status\n\nYou have met 240 dollars."
        quotes = quote_rag.split_into_quotes(text)
        self.assertEqual(len(quotes), 1)
        self.assertEqual(quotes[0]["head"], "Deductible status")
        self.assertIn("240 dollars", quotes[0]["text"])

    def test_blockquote_marker_stripped(self):
        quotes = quote_rag.split_into_quotes("> quoted line\n\nplain line")
        self.assertEqual(quotes[0]["text"], "quoted line")
        self.assertEqual(len(quotes), 2)

    def test_long_paragraph_wraps_at_sentences(self):
        text = "One. " * 60  # ~300 chars, under max_len default
        long_text = ("Sentence one is reasonably long here. " * 40).strip()
        pieces = quote_rag.wrap_sentences(long_text, 400)
        self.assertGreater(len(pieces), 1)
        self.assertTrue(all(len(p) <= 400 + 60 for p in pieces))
        _ = text


class IndexBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = quote_rag.build_index(ROOT / "sample-docs", None)

    def test_metadata(self):
        self.assertEqual(self.index["embedding"], "tfidf")
        self.assertEqual(self.index["version"], quote_rag.INDEX_VERSION)
        self.assertIn("idf", self.index)
        self.assertTrue(self.index["quotes"])

    def test_every_quote_has_file_and_tfidf(self):
        for q in self.index["quotes"]:
            self.assertIn("file", q)
            self.assertIn("text", q)
            self.assertTrue(q.get("tf"), q)

    def test_index_is_json_serializable(self):
        out = json.dumps(self.index, ensure_ascii=False)
        self.assertIn('"embedding"', out)

    def test_unreachable_ollama_falls_back_to_tfidf(self):
        # No local Ollama in the test environment; embed() must return None
        # and build must quietly stay on TF-IDF.
        self.assertIsNone(quote_rag.ollama_embed("hello", "some-model"))
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            self.assertEqual(
                quote_rag.build_index(tmpdir, "nomic-embed-text")["embedding"],
                "tfidf",
            )


class AskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = quote_rag.build_index(ROOT / "sample-docs", None)

    def finds(self, question: str, need: str, n: int = 5):
        scored = quote_rag.ask(self.index, question, n)
        self.assertTrue(scored)
        top_texts = " ".join(s["quote"]["text"] for s in scored)
        self.assertIn(need, top_texts, f"question={question!r}")
        return scored

    def test_question_about_denial_finds_co97(self):
        scored = self.finds("Why was the claim denied?", "CO-97")
        self.assertGreater(scored[0]["score"], 0.1)

    def test_deductible_question_finds_deductible_quote(self):
        self.finds("What's my deductible status?", "deductible")

    def test_appeals_question_finds_deadline(self):
        self.finds("How long do I have to appeal the denial?", "180 days")

    def test_manuscript_question_finds_chapter_info(self):
        self.finds("Which chapters are in the second draft?", "beach")

    def test_zero_overlap_question_scores_zero(self):
        scored = quote_rag.ask(self.index, "zzzqq-xyzzyx", 3)
        self.assertEqual(scored[0]["score"], 0.0)

    def test_results_sorted_best_first(self):
        scored = quote_rag.ask(self.index, "denied modifier claim", 5)
        scores = [s["score"] for s in scored]
        self.assertEqual(scores, sorted(scores, reverse=True))


class AnswerPromptTests(unittest.TestCase):
    def test_prompt_contains_question_and_sources(self):
        picked = [
            {"score": 0.9, "quote": {"file": "march-letter.txt",
                                     "head": "Appeals", "text": "180 days."}},
        ]
        prompt = quote_rag.build_answer_prompt("Can I appeal?", picked)
        self.assertIn("Question: Can I appeal?", prompt)
        self.assertIn("march-letter.txt (Section: Appeals)", prompt)
        self.assertIn("180 days.", prompt)
        self.assertIn("quotes don't contain", prompt)

    def test_collect_sources_respects_budget(self):
        def q(i):
            return {"file": "f.txt", "head": None, "text": (f"x{i:03d}" + "y" * 87)}

        scored = [{"score": 1 - i / 100, "quote": q(i)} for i in range(50)]
        picked = quote_rag.collect_sources(scored, max_total=400)
        # 400-char budget: four 90-char quotes fit, the fifth would be 450.
        self.assertEqual(len(picked), 4)
        self.assertEqual(
            len(picked), len({p["quote"]["text"] for p in picked})
        )


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        stdout, stderr = sys.stdout, sys.stderr
        import io
        out, err = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = out, err
        try:
            code = quote_rag.main(argv)
        finally:
            sys.stdout, sys.stderr = stdout, stderr
        return code, out.getvalue(), err.getvalue()

    def test_build_then_ask_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = str(Path(tmp) / "quotes.json")
            code, out, _ = self.run_cli(
                ["build", str(ROOT / "sample-docs"), "--store", store]
            )
            self.assertEqual(code, 0)
            self.assertIn("quotes", out)
            code, out, _ = self.run_cli(
                ["ask", store, "Why was the claim denied?"]
            )
            self.assertEqual(code, 0)
            self.assertIn("CO-97", out)
            code, out, _ = self.run_cli(["peek", store])
            self.assertEqual(code, 0)
            self.assertIn("claim-reference.txt", out)

    def test_ask_zero_overlap_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = str(Path(tmp) / "quotes.json")
            self.run_cli(["build", str(ROOT / "sample-docs"), "--store", store])
            code, out, err = self.run_cli(["ask", store, "zzzqq-xyzzyx"])
            self.assertEqual(code, 1)
            self.assertIn("No quotes matched", out)

    def test_missing_store_errors(self):
        code, _, _ = self.run_cli(["ask", "/nonexistent/quotes.json", "hi"])
        self.assertEqual(code, 2)


class PrivacyTests(unittest.TestCase):
    """No personal data should ever be committed with this project."""

    def test_sample_docs_carry_no_real_pii(self):
        for p in (ROOT / "sample-docs").glob("*"):
            text = p.read_text(encoding="utf-8", errors="replace")
            for forbidden in ("ssn", "@", "555-"):
                self.assertNotIn(
                    forbidden, text.lower(), f"{p.name} contains {forbidden!r}"
                )

    def test_no_secrets_in_tools(self):
        for p in (ROOT / "tools").glob("*.py"):
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("api_key", text.lower(), p.name)
            self.assertNotIn("sk-", text, p.name)


if __name__ == "__main__":
    unittest.main()
