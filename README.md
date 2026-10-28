# Ask Your Files AI Guide

A free, beginner-friendly manual for asking AI questions about **your own documents** — fully local, on your own computer.

Written in the plain-English, step-by-step style of Dylan Asdale's
*The Massive AI Manual*: like a friend would explain it, never condescending.

Published by **Asdale Dynamics, LLC**.

## What's inside

The manual lives as Markdown chapters in `docs/`:

| Chapter | File | What it covers |
| --- | --- | --- |
| 1 | `docs/01-why-pasting-fails.md` | Why pasting documents into chat fails once your pile grows |
| 2 | `docs/02-simple-retrieval.md` | Simple retrieval ideas: plain search, tagging, outlines |
| 3 | `docs/03-quote-file-rag.md` | Building a tiny "quote-file" RAG step by step (with Ollama) |
| 4 | `docs/04-folder-packing.md` | The folder-packing approach: one prompt, full folder |
| 5 | `docs/05-privacy-rules.md` | Privacy rules for personal files |
| 6 | `docs/06-when-to-doubt.md` | When an AI answer deserves doubt |
| 7 | `docs/07-first-project.md` | A guided first project, from empty folder to first answer |
| 8 | `docs/08-checklist.md` | A printable checklist for every Q&A session |
| 9 | `docs/09-glossary.md` | The glossary: every term, explained like a friend would |

Start with `docs/index.md`, which shows how the pieces fit together.

## The tools that come with it

- **`tools/quote_rag.py`** — the tiny quote-file RAG built in Chapter 3, ready to use.
  Searches your files for the quotes that actually answer your question
  (works fully offline without Ollama; better with Ollama installed).
- **`tools/build_site.py`** — the build script. Turns `docs/*.md` into a polished
  static HTML website in `site/`. No frameworks, no network, just Python.

This guide pairs well with two companion command-line tools:

- **folder-to-prompt-cli** — packs a whole folder into one prompt (see Chapter 4).
- **chat-export-archiver-cli** — saves your chat exports into a searchable archive.

## Requirements

- Python 3.9 or newer (no third-party packages needed)
- Optional: [Ollama](https://ollama.com) for the embedding + chat upgrade in Chapter 3

## Build the site

```bash
python3 tools/build_site.py
```

That writes `site/index.html` plus one page per chapter. Open `site/index.html`
in any browser — everything is local, no internet needed.

## Run the tests

```bash
python3 -m pytest tests/
```

or, if you don't have pytest:

```bash
python3 -m unittest discover -s tests
```

## Use the quote-file tool

```bash
# Build an index from a folder of .txt / .md files
python3 tools/quote_rag.py build ./sample-docs --store /tmp/quotes.json

# Ask a question (prints the best matching quotes)
python3 tools/quote_rag.py ask /tmp/quotes.json "What's my deductible?"

# With Ollama running, get a full answer from a local model
python3 tools/quote_rag.py ask /tmp/quotes.json "What's my deductible?" --answer
```

## Privacy, briefly

Everything here is designed to run **on your computer**. No telemetry, no
network calls (except optional, local Ollama requests to `127.0.0.1`), no
secrets or personal data baked into any file. See Chapter 5 for the rules.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
