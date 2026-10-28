# Chapter 7 — Your First Project: From Empty Folder to First Answer

Everything so far becomes one concrete project in this chapter. Budget: one
evening, zero dollars, no cloud accounts. By the end you'll have a
working local pipeline you built and ran yourself, and — the important part —
your first real, sourced answer about your own files.

## The project

> **"Question clinic": take one messy real folder, and make your next question
> about it answerable in under a minute — with a quote you can open and show.**

Pick a folder today: your insurance correspondence, your eBay returns threads,
one section of notes from work. Real documents, moderate volume.

## Milestone 1 — Set up the workspace (10 minutes)

```bash
mkdir -p ~/qclinic/docs ~/qclinic/builds
cp -r /path/to/your-real-folder/* ~/qclinic/docs/
```

Principles you're following (from Chapter 5): you copied, so originals stay
untouched — this work happens on redactable copies. Everything lives under one
`qclinic` folder — one place to back up, one place to delete.

**Convert what needs converting.** The quote-file tool reads `.txt` and `.md`.
For PDFs, do a text export (print-to-`txt` in many readers, or any local
desktop tool; scans with no text layer need OCR — try your OS's built-in tools
first). Don't perfect this part; convert three to five core documents, move on.

## Milestone 2 — Make the pile legible before any AI (15 minutes)

1. Write `~/qclinic/docs/INDEX.md` with one line per file (Chapter 2 format:
   date, filename, subject, tags).
2. Write `~/qclinic/docs/OUTLINE.md`: five bullets max, one per theme.

This is the step people want to skip. Do it anyway — it's 15 minutes, and it
makes every later step sharper: the index is what *you* read when search is
blurry; the outline is what the AI reads to know your pile's shape.

## Milestone 3 — Build and run the quote file (10 minutes)

Python is the only requirement:

```bash
cd ~/qclinic
python3 /path/to/this-guide/tools/quote_rag.py build ./docs --store builds/quotes.json
python3 /path/to/this-guide/tools/quote_rag.py ask builds/quotes.json "your actual question" --top 5
```

If you don't already have Ollama, the build marks the index as TF-IDF (Chapter 3)
and it still works — same commands, offline scoring.

While it runs, write down what surprises you. Most people are surprised
twice: by the goods (an answer in 8 ms) and by the misses (the quote you
*know* exists didn't score top). Misses teach the most. Nearly every miss is
one of: wrong file format, a paragraph far too long, or your question's words
don't appear in the document. Fix category three by re-asking with words the
document itself uses — this retraining of *your* asking instinct is the real
skill, worth more than any tool on its own.

Optional, only when Ollama is on your machine:

```bash
ollama pull nomic-embed-text
python3 tools/quote_rag.py build ./docs --store builds/quotes.json --embed nomic-embed-text
```

Same question again, and compare. Meaning-matching now helps when your words
and the document's differ.

## Milestone 4 — The first *sourced* AI answer (20 minutes)

Now the generation step — paste the passed quotes and *your* question into a
chat window or a local model and ask directly:

> "Here are 5 quotes I retrieved from my files, with their sources. My question:
> ⏎ Your question. Answer using only quotes you can see; say so for what's
> missing."

If you use a local model, the CLI does it:

```bash
python3 tools/quote_rag.py ask builds/quotes.json --answer "your actual question"
```

**Now the Chapter 6 reflex:** pick one non-obvious claim in the answer, open
the cited file, and read the sentence it came from. This is the moment it
clicks — first *verified* answer, fully on your machine, files untouched,
nothing left your computer. Take a breath. That was the whole loop.

## Milestone 5 — Name what you built (5 minutes)

You now own a pipeline with five pieces. Naming them is what makes them
transferable to the other folders in your life (the book draft, the eBay
ledger, the budget):

| Piece | What it is | Your file |
| --- | --- | --- |
| docs | the copies that get read | `~/qclinic/docs` |
| INDEX | one-line records, tags | `/INDEX.md` |
| OUTLINE | map of themes | `/OUTLINE.md` |
| builds | re-runnable indexes | `/builds/quotes.json` |
| the loop | search → quotes → answer → *verify* | later a habit, not a file |

Add your *next* folder on the list the same night (just the name; setup when
you get to it). Momentum comes from naming the next one now, at the exact
moment it's fresh.

## If something didn't work

- **"Indexed 0 quotes."** No `.txt`/`.md` files in the folder — see the
  conversion step in Milestone 1.
- **Scores all look mushy (~0.2 everywhere).** Your question probably uses
  words from your vocabulary, not the documents'. Re-ask with a document word
  ("explanation of benefits," the specific form name — actual letters).
- **The answer asserts with no quotes.** You're in `--answer` mode without
  local model agreement, or the top quotes really came from
  something-else-but-plausible. Scroll up: the quote list is always displayed
  before the summary — trust the list, not the prose.
- **Everything works but feels slow.** You don't need speed. The point is that
  it *runs* — even 10× "slower" beats pasting the whole library every session
  (Chapter 1's counting problem).

Keep going with [Chapter 8](08-checklist.md): the one-page checklist you can
print and tape to your desk, so the first project becomes the everyday way.
