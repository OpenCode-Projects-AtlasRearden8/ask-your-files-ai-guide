# Chapter 8 — The Session Checklist

Print this page, or keep it in your notes app. It compresses Chapters 1–7 into
something you can follow on a low-energy day, when the pile is messy and the
question feels big. Two checklists: one for every session, one for setting up
a brand-new folder.

## Checklist A — Every Q&A session

1. **State the question as if to a friend.** If it needs a second run-through,
   it needs rewriting. Plain sentence: *"My question is: ___."*

2. **Choose the route** (one line below each):
   - [ ] **Already know roughly where?** → Chapter 2 search first: one unique
     phrase, not one vibe.
   - [ ] **Question spans several files?** → quote file ask (Chapter 3).
   - [ ] **Question spans the *whole* pile?** → folder pack (Chapter 4).

3. **Favorite place to look: your own quotes, not a new paste.** If an old
   `quotes.json` already covers the folder, ask it first; it's faster than
   repacking.

4. **Before any paste (out to a screen or to your own notes):**
   - [ ] No passwords, card numbers, logins, or one-time codes — the absolute
     rule (Chapter 5).
   - [ ] Names, account numbers, DOBs, addresses redacted to placeholders.
   - [ ] Smallest sufficient set — one paragraph beats one letter beats one folder.

5. **When an answer arrives:**
   - [ ] One claim picked; source opened; line read.
   - [ ] Words it introduced that *you* have never seen in your own files,
     greeted as a stranger (Chapter 6).
   - [ ] Felt like "perfectly smooth"? Reread the ragged parts of your source docs.

6. **Close the loop:**
   - [ ] Question → answer → source: save one line to the folder's `NOTES.md`
     (date, question, file that settled it).
   - [ ] New file added to pile? One line in `INDEX.md` (Chapter 2) now, not later.

## Checklist B — A new folder, once

1. **Copy, never move.** The originals stay exactly where they were.
2. **Convert to `.txt`/`.md`** everything you actually read the last time you
   needed this folder (three to five files — do not convert everything).
3. **Write `INDEX.md`** — one line per file: date, filename, subject, tags.
4. **Write `OUTLINE.md`** — <= 5 bullets, one per theme.
5. **Build the quote file** — `python3 tools/quote_rag.py build docs --store
   builds/quotes.json` — and ask it one question you *know* the answer to, to
   hear the tool working.
6. **Redact the copies for anything you'd paste** — placeholders, per Chapter 5.
7. **Name the next folder** to repeat this on. Stop here for the night; the
   next folder can wait past the dinner table.

## Ask-the-tool quick card (Chapter 3 commands)

| Situation | Command |
| --- | --- |
| Build / rebuild an index | `python3 tools/quote_rag.py build ./docs --store builds/quotes.json` |
| Find quotes (offline) | `python3 tools/quote_rag.py ask builds/quotes.json "my question"` |
| More results to skim | add `--top 10` |
| With meaning-based ranking | rebuild `--embed nomic-embed-text` (Ollama) |
| Full drafted answer, local | `ask ... --answer` (optionally `--model llama3.2`) |

## The escape hatches (when a session goes sideways)

- Question got bigger than the pile? Bubble up to a professional — Chapter 6's
  stakes map tells you when.
- Tool output felt blind? Two search phrases by hand (Chapter 2); if *search*
  finds the quote but the tool didn't, that's a fixable index, not a you.
- Energy ran out? Checklist A step 6 (one notes line + one index line) is the
  smallest possible "closed" — close it and rest.

## In one sentence

> One honest question, one small chosen retrieval, one source verified, one
> line written down.

**Next:** [Chapter 9 — Glossary](09-glossary.md): every term from this manual
in one friendly place.
