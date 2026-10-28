# Chapter 5 — Privacy Rules for Personal Files

You're going to paste some of your own documents into AI conversations. Good
documents to paste: contracts, manuals, manuscripts, meeting notes, letters
that have already been through an appeals process. Documents to keep away:
anything you'd be uncomfortable finding, quoted, in someone else's hands.

The principles in this chapter are short, and they're the whole policy:

> **Rule 1 — Local first.** If the tool can run on your computer, run it there.
> Every tool in this guide does. A local model can't leak what it never sees.

> **Rule 2 — Minimum sufficient data.** Paste the smallest set that can answer
> the question. Ask "which paragraph do I need?" before "should I paste the
> file?" — often it's one paragraph, and Chapter 2's search finds it.

> **Rule 3 — Redact by default.** Names, account numbers, member IDs, dates of
> birth, full addresses, phone numbers: replace with placeholders before
> pasting. `Policy #REDACTED-01`, `my spouse`, `my primary clinic`. The AI
> answers your question just as well with placeholders 99% of the time.

> **Rule 4 — Never paste credentials or money.** Passwords, API keys, full
> payment card numbers, bank logins, one-time codes. If a document contains
> one, redact the line. This rule is absolute; there's no "just this once."

> **Rule 5 — Understand the tool before the file.** Cloud chat tools vary:
> some train on your messages, some promise otherwise, some have per-chat
> settings. When in doubt, redact more, or take the local route. Corporate
> accounts can have separate logging policies from personal ones — don't mix
> them.

## The redaction habit, made concrete

Keep a tiny scratch file (or just your editor's find-and-replace) with
placeholders you reuse, so redaction takes thirty seconds:

| Original | Placeholder |
| --- | --- |
| `John Asdale` | `I / the patient` |
| `Bill Henderson` (third party) | `Person A` |
| `Account 4471-0092-33` | `Account ###-END-33` |
| `DOB 03/14/74` | `DOB [redacted]` |
| `123 Maple Street` | `my home address` |

Two tricks that make this sustainable:

- **Keep the tail digits.** You often need the *fact that* two documents share
  an account, not the number itself. `###-END-33` keeps the match, drops the ID.
- **Redact the copy, never the original.** Work from a local copy when a
  document will be pasted at all. The original files stay intact, exactly as
  filed.

## What "local" actually buys you

Local-first isn't only a privacy virtue; it *removes decisions*. When the
model, the embeddings, and the index all live on your machine:

- no upload step exists to get wrong,
- no account, no terms-of-service gray area, no retention setting,
- the index file (`quotes.json`) is just a file you can delete, like any other.

The trade-off is real: local models, especially small ones, are less polished
than the big cloud models. For quote-reading and summarizing, they're usually
plenty — and when they're not, Rule 2 (minimum data, redacted) is your cloud
escape hatch, used deliberately.

## Personal-data radar (the 60-second version)

Before any paste, scan for: names of other people, dates of birth, account or
member numbers, street addresses, phone/email, anything medical-visit-shaped,
anything third-party-named, anything you'd be sad to find screenshot in an
unexpected place. If you see placeholders in your pasted text and the question
still works — pause and confirm — you're in good shape. If the question only
works with the private detail visible, that's a sign the question itself might
be one for a professional, not a chat window (see Chapter 6).

## A note on scanned documents and photos

Scans and photos of documents carry all the same personal data as the paper —
and sometimes more (a photo of a bill on your desk may include handwritten
notes, or fragments of other mail). Redact or crop *images* too, and remember
that OCR tools (including the ones that would let you use Chapter 3 on a scan)
may themselves be cloud services. Prefer local OCR (many local tools exist)
when the pages are sensitive.

## In one sentence

> Run it local, paste the least, redact by habit, and never let credentials or
> money across the line — pretty soon it's a reflex, not an effort.

**Next:** [Chapter 6 — When answers deserve doubt](06-when-to-doubt.md): the
judgment layer, protecting everything above.
