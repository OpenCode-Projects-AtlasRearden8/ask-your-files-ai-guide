# Chapter 3 — Build a Tiny Quote-File RAG

"RAG" — retrieval-augmented generation — sounds enterprise. The idea is
actually small: before asking an AI to answer, *fetch the few quotes from your
files that answer the question*, and paste just those into the prompt. It's the
Chapter 1 rule on autopilot: bring the page, not the library.

In this chapter you'll use the tool that ships with this guide,
`tools/quote_rag.py`, and understand every moving part as we go.

## The idea in one breath

Your documents get chopped into **quotes** — paragraph-sized pieces, each one
small enough to quote honestly and short enough for a prompt. Each quote gets
scored against your question for relevance, top-scoring quotes get shown, and
(optionally) get copied into a local model's prompt so it drafts an answer
*with the quotes visibly in front of it*.

Because each step is a script you can read, there's no magic: if the answer is
wrong, you can see *which quote won* and *why*.

## Step 0: Check what you have

Everything works with plain Python — no internet, no accounts, no packages.
If you have [Ollama](https://ollama.com) installed and running, the tool also
uses local **embeddings** (see below) and lets a local model draft full answers.
Check either way:

```bash
python3 --version   # need 3.9+
ollama list          # optional; errors here are completely fine
```

## Step 1: Build the quote file

A *quote file* is just a JSON index of your pile — pieces of text from your
documents plus metadata. Build one from any folder of `.txt` and `.md` files:

```bash
python3 tools/quote_rag.py build ./sample-docs --store quotes.json
```

You'll see a line like:

```text
Indexed 18 quotes from 5 file(s) (tfidf) -> quotes.json [0.00s]
```

Peek inside with any text editor and you'll see the structure:

```json
{
  "version": 1,
  "source": "sample-docs",
  "embedding": "tfidf",
  "idf": { "co": 3.25, "denied": 3.25, "...": "..." },
  "quotes": [
    { "file": "claim-reference.txt",
      "text": "This claim was denied under code CO-97: ...",
      "head": "Why you were denied",
      "tf": { "co": 3.25, "97": 3.25 } }
  ]
}
```

What's happening under the hood (worth knowing, worth being able to explain):

- **Chunking.** Files are split at blank lines into paragraph-sized pieces.
  Every piece keeps a pointer to its source file — that's how "where did this
  come from?" stays answerable.
- **Marked quotes.** A paragraph starting with `` > `` (or a `## heading`)
  records its heading as `head`, so titles can help ranking later.
- **JSON, not a database.** A human-openable index you can edit, back up, and
  diff. When it works, you trust it; when it doesn't, you can see it.

## Step 2: Ask

```bash
python3 tools/quote_rag.py ask quotes.json "Why was the claim denied?"
```

And get back the most relevant quotes, scored:

```text
Top quotes for: 'Why was the claim denied?'  (searched in 0 ms)

[0.33] claim-reference.txt — Why you were denied:
  This claim was denied under code CO-97: "the service billed is covered,
  but the modifier it was billed with is inconsistent with the service."

[0.15] claim-reference.txt:
  Sample claim reference letter — fictional, for testing the guide's
  tools.

[0.10] february-letter.txt — What happened:
  Today we received your claim for the same-day clinic visit on February
  9. We have paid the preventive portion and applied the visit to your
  deductible.
```

Each score is a similarity. Notice how much accountability this buys: every
claim in the final answer now has a *visible, checkable source quote* — a huge
upgrade over big pastes, where documents blur together.

## Step 3: The optional Ollama upgrade

If you ran `ollama pull nomic-embed-text` (a small local embedding model), the
tool can switch from the built-in TF-IDF scorer to real embeddings:

```bash
# once, one download
ollama pull nomic-embed-text

# rebuild the index (it will notice the model is available)
python3 tools/quote_rag.py build ./sample-docs --store quotes.json --embed nomic-embed-text

# rankings improve for meaning, not just word overlap:
python3 tools/quote_rag.py ask quotes.json "Can I fight this decision?"
```

**What changed.** TF-IDF matches words ("appeal" vs "fight" score differently).
Embeddings map meaning: *fight this decision* lands near *appeal* even though
they share no words — before the upgrade, TF-IDF politely reports "No quotes
matched" for that question, which is exactly the honest gap this fills. For a few hundred quotes, TF-IDF is usually fine and
always instant; for a few thousand, embeddings earn their keep. Best habit:
rebuild with `--embed` where you have it, keep `--store` files buildable on any
machine.

And now the full RAG — answer, not research — using a local chat model:

```bash
ollama pull llama3.2
python3 tools/quote_rag.py ask quotes.json "Can I fight this decision?" --answer --model llama3.2
```

The tool asks the local model with a prompt like:

```text
Answer ONLY using the quotes below. If they don't contain the answer, say
exactly: "The quotes don't contain that."

Question: Can I fight this decision?

Quote from march-letter.txt (Section: Appeals):
You may appeal within 180 days of the denial date.
```

`--answer` never skips the quote step, and never fetches from the network.
It's the same quotes, plus a local model asked to write the paragraph for you.

## Read the tool's limits out loud

- **It only sees `.txt` and `.md` files.** For PDFs, first do a text export;
  Chapter 7 folds that step into the workflow.
- **Whole-file keywords beat subtle meaning**, sometimes. Try `--top 20` and
  skim more quotes; a small tool is meant to be reread.
- **Long files in one paragraph drench it.** Chunking is the guess about
  paragraph size; if a paragraph is a full page, split it manually.

## Why this is worth building yourself

Every piece is small and open: chunks, scores, JSON. When the tool is yours,
you learn the actual shape of *retrieval* — which is the one skill every RAG
system (including giant enterprise ones) shares. And it's a pattern you keep:
the same quote-file idea will power the **chat-export-archiver-cli** companion
tool, where your archived chats become a searchable quote file of their own.

## In one sentence

> Chop your files into quotes, score them against your question, paste only the
> winners — the paste stays small because a script chose it.

**Next:** [Chapter 4 — Folder packing](04-folder-packing.md): when the question
really does need the *whole pile* at once — and a way to do that safely too.
