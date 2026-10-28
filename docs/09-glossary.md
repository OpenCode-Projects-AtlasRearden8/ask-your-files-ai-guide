# Chapter 9 — Glossary

Every term used in this manual, explained like a friend would — casually,
accurately, and in one or two sentences each.

**Chunk** — A piece of a document, sized to be quotable. In this guide,
chapters of your pile get chopped into paragraph-sized pieces, and each piece
is one "chunk." Chunking is where a RAG system's quality starts: wrong-sized
chunks mean ambiguous quotes.

**Context window** — An AI model's working desk. Everything the model can see
for one reply — your prompt, pasted documents, the conversation so far — must
fit in this memory. Pasting your whole library eventually can't fit, which by
Chapter 1 is why we retrieve.

**Embedding** — A way of turning text into a list of numbers such that
similar-meaning texts land near each other. The local model `nomic-embed-text`
(Chapter 3, with Ollama) makes these embeddings on your machine; scoring a
question against quotes becomes a fast similarity comparison.

**Folder packing** — Bundling a folder's files into one prompt, each file
separated by a header (Chapter 4). Great for cross-file questions over small
piles; skip it when the pile is big — that's a quote-file problem.

**Hallucination** — When an AI states something that isn't true or isn't in
your documents, in fluent confident prose. Not lying exactly — more decorating
(Chapter 1). The cure you own: quotes, visible sources, verification (Chapter 6).

**Index (document index)** — A helper file that says what your pile contains.
`INDEX.md` is your hand-made one (Chapter 2); `quotes.json` is the tool-built
one (Chapter 3) — a list of chunks with their source files.

**JSON** — A plain-text structured data format, openable in any editor. Your
quote file is JSON on purpose: no database to trust, no binary to damage, easy
to back up, diff, and delete.

**Ledger** — This guide's nickname for the one-file-per-folder index
(`INDEX.md` from Chapter 2: date, filename, subject, tags — one line each).

**Local-first** — Designing so everything runs on your computer: no uploads,
no accounts, no retention settings to trust, no data leaving your machine
except when you deliberately paste (Chapter 5's Rule 1).

**Lost-in-the-middle** — A documented behavior where models pay less attention
to the middle of very long inputs. Important only because it's invisible: pastes
can silently miss detail while sounding confident.

**Ollama** — Free software that runs open AI models on your own computer,
locally. In this guide it optionally provides embeddings (`nomic-embed-text`)
and local answering (`llama3.2`) for the quote-file tool.

**Quote file** — The JSON index this guide builds. Pulls the quotable chunks of
your files — hence the file's function: a searchable shelf of quotable pieces.

**RAG (retrieval-augmented generation)** — Ask-anything pattern: *retrieve* the
small relevant pieces of your documents first, then *generate* an answer with
those pieces visibly in the prompt. This entire guide is one friendly version
of it.

**Redaction** — Replacing private details (names, numbers, addresses) with
placeholders before pasting. Habit, not event — keep placeholder text handy
(Chapter 5).

**Retrieval** — Finding the right piece of your pile for a question, before
any generation happens. Chapter 2's search, Chapter 3's quote file, and
Chapter 4's packing are all retrieval methods at different rungs of effort.

**Scoring** — Giving each quote a number for "how relevant to this question?"
With TF-IDF it's word overlap math; with embeddings it's meaning-space
distance; with your eyes it's `--top 20` and a skim.

**Source path** — The file a quote came from (`docs/eob-2024-02-11.txt`). The
core safety feature of the whole pipeline: every answer should be traceable to
one. Chapter 6's first verification move is *always* "which file?"

**TF-IDF** — The classic word-overlap scoring method built into the quote-file
tool as its offline default: terms counted per quote scaled by how rare they
are across your pile ("CO-97" beats "claim"). No model, no download, works
anywhere Python runs.

**Tag** — A short word you deliberately associate with files (shown in your
ledger as `tags: ...` in Chapter 2). Cheap and hand-made; they make search
specific and give the chapter-3 index the vocabulary of your pile.

**Token** — The units models read and write, roughly word-chunks. Context
windows are measured in thousands of tokens; your pastes are too. Why pasting
fails at scale is simply that tokens in documents outnumber tokens on the desk.

**Topical outline** — A bulleted map of your pile's themes (`OUTLINE.md` in
Chapter 2). Answers questions by itself, seeds your tags, and doubles as the
cover sheet pasted at the top of any AI session.

**Verification (closing the loop)** — The one claim, one source-file, one real
read (Chapter 6). The habit that turns an AI from a plausible-sounding stranger
into a useful research assistant.

That's the whole book. If you made it here having run your first quote-file
ask and checked one source quote, you have the skill this manual exists to
teach. Everything else is practice — and [Chapter 7](07-first-project.md)
will be waiting the next time a new folder shows up in your life.
