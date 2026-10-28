# STATUS.md

**Project:** Ask Your Files AI Guide
**Owner:** Asdale Dynamics, LLC (Dylan Asdale)
**Date:** 2026-10-27
**License:** MIT — see [LICENSE](LICENSE)

## What was built

A beginner-friendly, local-first manual for asking AI questions about your own
documents, delivered two ways plus two working tools:

- **`docs/`** — 10 Markdown chapters (start page + 9 numbered chapters):
  1. Why pasting fails at scale
  2. Simple retrieval ideas (plain search, tagging, outlines)
  3. Building a tiny quote-file RAG with Ollama (optional upgrade, offline fallback)
  4. The folder-packing approach (pairs with `folder-to-prompt-cli`)
  5. Privacy rules for personal files
  6. When answers deserve doubt
  7. Step-by-step first project ("question clinic")
  8. Session checklist (one per session + one per new folder)
  9. Glossary
- **`site/`** — the rendered static HTML site, one page per chapter plus a
  sticky chapter sidebar, warm book-like styling, link-checked, zero external
  assets, built by the script below. Committed so it can be browsed as-is.
- **`tools/build_site.py`** — stdlib-only Markdown→HTML site builder
  (`--check` mode verifies every internal link resolves).
- **`tools/quote_rag.py`** — the tiny quote-file RAG written in Chapter 3:
  `build` (chunks .txt/.md into paragraph quotes, JSON index), `ask`
  (prices quotes against your question; TF-IDF offline, local Ollama
  embeddings when available), `peek`, and optional `--answer` mode that gives
  the quotes to a local Ollama chat model with a "quotes only" prompt.
  Never touches the network except optional `127.0.0.1` (Ollama) calls.
- **`tests/`** — 50 tests (unittest, pytest-compatible) covering the Markdown
  converter, site build + link check, chunker, TF-IDF scoring, CLI end-to-end
  flows, privacy scans (no secrets/PII in samples/tools).
- **`sample-docs/`** — five small fictional sample files so any command in the
  README runs out of the box.
- **`README.md`, `LICENSE`, `.gitignore`** — directory, scripts, MIT license.

Companion tools referenced by the manual (separate projects, not included):
`folder-to-prompt-cli` (Chapter 4) and `chat-export-archiver-cli` (future).

## How to run it

```bash
# Build the static site (reads docs/, writes site/, checks links)
python3 tools/build_site.py            # or with link check:
python3 tools/build_site.py --check

# Run the tests
python3 -m pytest tests/               # or: python3 -m unittest discover -s tests

# Try the quote-file RAG on the included samples
python3 tools/quote_rag.py build ./sample-docs --store /tmp/quotes.json
python3 tools/quote_rag.py ask /tmp/quotes.json "What's my deductible?"
python3 tools/quote_rag.py peek /tmp/quotes.json

# Optional, with Ollama installed and running
ollama pull nomic-embed-text
python3 tools/quote_rag.py build ./sample-docs --store /tmp/quotes.json --embed nomic-embed-text
python3 tools/quote_rag.py ask /tmp/quotes.json "Can I fight this decision?" --answer --model llama3.2

# Read the site
open site/index.html   # linux: xdg-open site/index.html
```

Requirements: Python 3.9+ only (no third-party packages). Ollama optional.

## Verification results (all run locally, 2026-10-27)

| Check | Result |
| --- | --- |
| `python3 -m pytest tests/ -q` | **50 passed**, 0 failed, 0 skipped |
| `python3 tools/build_site.py --check` | Built 10 pages, **link check passed** |
| `quote_rag.py build ./sample-docs` | 18 quotes from 5 files, TF-IDF mode |
| `quote_rag.py ask "What's my deductible?"` | Top hit: the deductible paragraph (0.38), correct answer surfaced |
| `quote_rag.py ask "Why was the claim denied?"` | Top hit: the CO-97 denial paragraph (0.33) |
| `quote_rag.py ask "zzzqq-xyzzyx"` (no overlap) | Honest "No quotes matched" message, exit code 1 |
| `quote_rag.py ask ... --answer` without Ollama | Clean failure message, exit code 1 (no crash) |
| Offline behavior | No network used in any default path (verified in tests) |
| Secrets/PII scan | No API keys, tokens, or personal data in any file (test-enforced) |

Known environment note: Ollama was **not** installed in the build environment,
so the embedding and `--answer` paths were verified through their offline
fallbacks and error handling, not against a live local model.

## Known gaps

- The Markdown converter supports the constructs this manual uses (headings,
  fenced code, blockquotes, lists one nesting level deep, tables, inline
  code/bold/italic/links, checkboxes). Setext headings, footnotes, and nested
  tables are out of scope; unknown constructs pass through as plain text.
- `quote_rag.py` reads `.txt`/`.md` only; PDF/DOCX readers are deliberately out
  of scope (Chapter 7 shows the export step instead).
- Embeddings and `--answer` need a running local Ollama; without it the tool
  degrades to TF-IDF and message-only guidance (tested).
- The site has no JavaScript (by design: print/read-first); anchor jumps use
  plain HTML fragments only.
- `chat-export-archiver-cli` is referenced as a future companion and does not
  exist yet in this repository.
