# Chapter 4 — The Folder-Packing Approach

Sometimes the honest answer is: you genuinely need the *whole folder* at once.
A cross-document question — "bottlecap chapter appears in which of my drafts?"
"which letters ever mention June 14th?" — can't be answered from one quote at a
time. Folder packing is the technique: one script turns a folder into one
prompt, everything dated, named, and compact.

This chapter tells you when to pack, how to pack well, and how the companion
tool **folder-to-prompt-cli** fits.

## When packing is the right call

Pack when the question spans files rather than living inside one:

- **Inventories** — "list every claim amount across all replies."
- **Name-driven maps** — "which files mention X?" (then Chapter 2 search.
  Packing finds fuzzy as well as exact matches.)
- **Small piles that fit.** If your folder has ~15 short files, packing and
  asking usually beats building an index.

Skip packing when the pile is long, is mostly boilerplate you'll never need,
or contains anything too personal to paste (Chapter 5 — loud).

## How a good pack looks

A good pack is a plain-text bundle, files separated by metadata headers so the
model (and you, months later) can trace any line to its source:

```text
=== FILE: sample-docs/eob-2024-02-11.txt (11 Feb 2024, 412 chars) ===
First paragraph of my explanation-of-benefits letter...
Second paragraph...

=== FILE: sample-docs/eob-2024-03-05.txt (5 Mar 2025, 380 chars) ===
...
```

Why this style works better than `cat *.txt > one.txt`:

- **Clear fences.** Models treat `=== FILE:` markers as boundaries, and the AI
  can mention files by name in its answer.
- **Sizes visible.** A 400-char file is skimmable; knowing size bounds the
  model's guess about what's worth opening.
- **Dates resolve** "which one was newest?" in one step.

## The workflow, end to end

Our guide ships with a *minimal* packer below you can type in ten minutes, and
the companion tool **folder-to-prompt-cli** automates the polished version
(extensions filtering, file-type detection, redaction lists, clipboard copy):
one command, your whole folder in one prompt, ready to paste or file.

```bash
# with the companion tool installed:
folder-to-prompt ./my-docs --out packed-prompt.txt --ask "$(cat question.txt)"
```

## A minimal packer you can own

No companion tool? Here's the same idea in ~12 lines of Python you can put in
your own `bin` folder, named `pack.py`:

```python
#!/usr/bin/env python3
"""pack.py — bundle a folder of .txt/.md files into one prompt."""
import sys, pathlib

folder, out = pathlib.Path(sys.argv[1]), sys.argv[2]
parts = []
for f in sorted(p for p in folder.rglob("*") if p.suffix.lower() in {".txt", ".md"}):
    text = f.read_text(encoding="utf-8", errors="replace").strip()
    rel = f.relative_to(folder)
    parts.append(f"=== FILE: {rel} ({len(text)} chars) ===\n{text}\n")
pathlib.Path(out).write_text("\n".join(parts), encoding="utf-8")
print(f"Packed {len(parts)} files -> {out} "
      f"({sum(len(p) for p in parts)} chars total)")
```

```bash
python3 pack.py sample-docs packed-prompt.txt
```

Read what it does: it walks the folder, keeps only the extensions you care
about, and writes one header per file. That's it — no network, no magic. Paste the output into your next chat as one
message.

## The packer's guardrails (small, and worth keeping)

1. **Exclude before you ever pack.** Decide which folders are off-limits
   *first* — for most people: anything with `budget`, `ledger`, tax, or health
   records in the path. Your packer (and the companion tool's `--exclude` flag)
   should skip them by rule, not by memory.
2. **Keep a character budget.** A pack that's too big silently reintroduces the
   Chapter 1 problems. If the whole bundle is over roughly 20–30k words,
   you don't have a packing problem — you have a quote-file problem, and
   Chapter 3 is your friend again.
3. **A copy stays in your folder.** The pack is just another file. If you keep
   it (`packed-prompt.txt`), every question already has its file-visible
   source archive; save the *answer* next to it and you have hand-made provenance.

## Where chat-export-archiver-cli fits

The same alias exists in reverse: your AI **chats themselves** are documents —
the questions you asked and the answers you got. Saving them, trimming the
noise, and accumulating them into one searchable archive turns your AI history
into a first-class quote file (Chapter 3's format works great). That's exactly
what the companion tool **chat-export-archiver-cli** does, tidily, offline. End
of the loop: *your questions about your files become files you can ask about.*

## In one sentence

> When a question spans the whole pile, pack the pile into one honest,
> headered prompt — and keep packing as a conscious, deliberate move, not a
> habit.

**Next:** [Chapter 5 — Privacy rules](05-privacy-rules.md): the rules to keep
personally identifying or sensitive material off the pasteboard entirely.
