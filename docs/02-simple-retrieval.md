# Chapter 2 — Simple Retrieval: Search, Tagging, Outlines

Nothing in this chapter requires installing anything. If you can use the
search box in your file manager, you can do everything on this page. These
three habits — plain search, tagging, and outlines — are genuinely undervalued:
for most personal-document questions, they solve the whole problem, and even
when they don't, they make every later chapter work better.

## Idea 1: Plain search, done well

Your operating system already ships a full-text search engine (macOS Spotlight
or Finder search, Windows Explorer search, Linux desktop search). The trick is
using it like a professional, not like a new roommate looking for keys.

**Search by quote, not by topic.** Instead of asking "insurance," search a
phrase only that letter could contain: `"panel year 2026"` or `"denial code
CO-97"`. Unique word combos beat single common words every time.

**Search inside, not just among.** Make sure the tool indexes *file contents*,
not just filenames. On Windows, Explorer's "File contents" option; on macOS,
Finder's `⌘F` then "find by Content". If your PDFs aren't found, it's because
scans have no text layer — that's an OCR problem, and the fix plan is in
Chapter 7.

**Narrow by name pattern.** `2024-02*` finds everything from one month.
`letter*contract*` beats sorting through screenshots and selfies.

**Save the query.** If you'll ask it monthly (bills, quarterly taxes), save the
search or keep a `searches.txt` file with your favorite query syntax.

## Idea 2: Tags and a plain "ledger" file

Tags are just words you commit to writing on documents, in filenames or inside
a small index file. Start with a **ledger** — a single `INDEX.md` (or
`INDEX.txt`) file at the top of your document folder. One line per document:

```text
2024-02-14 | insurance-letter.pdf | claim denial | tags: CO-97, same-day-clinic, appeal
2024-03-01 | refund-email.txt     | seller reply | tags: ebay, return-window
```

Three columns, or fewer — a date, the filename, and free-form words. You've
just created a file that's trivially searchable *and* perfectly useful as AI
fodder, because it's a hand-made index of your pile. When a folder has an
`INDEX.md`, both Chapter 3's quote file and Chapter 4's folder packing
immediately get smarter: the AI sees your own labels.

Rules that make a ledger survive real life:

- **One line per file, always.** No multi-line rows. Lines are cheap to add.
- **Date first, ISO format** (`YYYY-MM-DD`), so sorting shows history.
- **Tags lowercase** and short; you'll type them again tomorrow.
- **Never delete a line** — if a file's old, mark it `archived` in tags.

## Idea 3: Topical outlines

When you know *what to look at* but not *where*, an outline is a map of your
pile you make once and reuse forever. Take your doc set, and write (or let an
AI help you draft from filenames only — never paste content!) one page:

```text
OUTLINE.md — What's in my paper pile
1. Billing and insurance
   1.1 Explanation-of-benefit letters 2024 (5 files, folder /insurance/eob-2024)
   1.2 The CO-97 denial story: what happened, letters, deadlines
2. The book manuscript (folder /manuscript)
   2.1 Chapters done: 1–4. Chapter 5 needs scene in revision.
3. eBay inventory and returns
   3.1 Listing templates. 3.2 Return-window rules I care about.
```

An outline earns rent three times:

1. **It answers questions itself.** "What did chapter five say again?" is
   answered by a glance, not a search.
2. **It seeds your tags** — everything in the outline becomes a tag word.
3. **It's the perfect cover letter for the AI** — paste the outline at the top
   of any session, and now the model knows your pile's shape so it can ask you
   for specifics instead of guessing.

## The cheap pipeline, assembled

Your document reflex after this chapter, before reaching for the AI at all:

1. Open search. Try two unique-phrase queries.
2. If it works, done — skim the found quotes.
3. If not, open `INDEX.md`, check what the pile itself knows.
4. Still fuzzy? Add a line to the outline, then continue.

Notice: the AI hasn't been involved yet. That's the point. Search is instant,
free, and private. Chapter 3 walks you into the next rung — when search isn't
enough and the pile is too foggy — with a real, working, offline tool you can
build in twenty minutes.

## In one sentence

> Search for phrases, tag with a one-file ledger, keep an outline — and you'll
> often never need to paste anything at all.

**Next:** [Chapter 3 — The quote-file RAG](03-quote-file-rag.md), where you
build a little search index that *you own*, run by a script that never leaves
your computer unless you tell it to.
