# Chapter 1 — Why Pasting Fails at Scale

## The paste era (and why we start there)

When you first try an AI assistant, pasting feels like a superpower. You copy a
two-paragraph email, ask "what tone is this?", and get a real answer in three
seconds. It works so well that you start pasting bigger things: the whole
contract. The whole paper. Then the whole *filing cabinet*.

Then one day you paste everything you own, hit Send, and the AI tells you —
politely or not — that it can only read part of it. Or worse, it reads it all
and gives you an answer that quietly ignores half of what you sent.

You didn't do anything wrong. You just outgrew the paste. This chapter explains
exactly why that happens, so the fix in later chapters makes real sense.

## The three failure modes of big pastes

### 1. The context window runs out

An AI model doesn't read your document like a person holds a page. It holds
everything in a workspace called the **context window** — think of a desk that's
only so big. Your pasted files, the conversation so far, and the AI's internal
instructions all sit on that desk together.

- Paste three pages? Fine. Lots of desk space left.
- Paste three hundred pages? The desk fills. Either the paste is refused, or —
  this is the sneaky part — old messages start falling off the far edge and the
  model never sees them again.

Context windows keep growing, which helps, but your file pile grows faster.
Insurance letters accumulate. Whatever the desk size, at scale the paste loses.

### 2. Attention thins out in the middle

Even when everything *fits*, models pay somewhat less attention to the middle
of a very long paste — researchers call this the "lost in the middle" problem.
The beginning and end of your document pile tend to get more weight. So the
question "what did my February letter say?" might get answered from a summary of summaries the model improvised, not from the actual
February letter buried mid-paste.

You will experience this as: *the answer sounds right, but detail from the
middle is missing or subtly wrong.* That's the most dangerous failure, because
nothing announces it.

### 3. Drift and decoration

At large scale, the model starts to drift: it blends your four similar letters
into one letter with a composite date, or borrows confidently from the *general
way contracts talk* rather than from what *your* contract says. With enough
material in context, a model's habit of filling gaps with plausible-sounding
words (what Chapter 6 calls the **reason-to-doubt zone**) gets harder to see.

## The costs nobody bills you for

Even when a big paste "works," you pay in three currencies:

1. **Time.** Selecting, scrolling, pasting — every session, forever. At
   two minutes per milestone, a hundred sessions costs you real recharge time.
2. **Accuracy.** Have you *ever* pasted the complete, current version? Any
   missing page quietly corrupts the answer.
3. **Privacy.** Every paste is a copy of your personal data leaving your
   computer (Chapter 5 gives rules for that). With cloud AI, each paste is a
   decision you have to re-make each time.

## The mind-shift: don't paste the library — bring the page

Here's the whole manual in one beat: **the answer to almost any of your
questions lives in a handful of quotes — a letter, a paragraph, a table row.**
You don't need to deliver the library to the AI. You need a way to find the right
*page* and hand it over.

That skill is called **retrieval**, and the rest of this book is a ladder of
retrieval methods that climb from dead-simple to genuinely powerful:

1. Plain search, tagging, outlines — no code, today (Chapter 2)
2. A tiny "quote file" search index you build with a script (Chapter 3)
3. Folder packing — when you truly need the *whole* folder in one prompt
   (Chapter 4)

Each rung uses a bit more tooling but solves a bigger pile. And every rung keeps
the paste *small and chosen*, which is what keeps the answer clean.

## In one sentence

> Pasting works until your pile doesn't fit on the AI's desk — so stop carrying
> the library around and start fetching the page that matters.

**Next:** [Chapter 2 — Simple retrieval ideas](02-simple-retrieval.md) — three
things you can do in fifteen minutes with the tools already on your computer.
