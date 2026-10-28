# Ask Your Files AI Guide

*A manual for asking AI questions about your own documents — fully local, fully yours.*

## Who this is for

You have a pile of documents. Medical bills and insurance letters. A book
manuscript in progress. Buyer notes from eBay. Meeting notes from work. A shoebox
of scanned paperwork. And you have an AI assistant — whatever kind, however you
run it — and a feeling that it could help you *ask better questions* about all
those files. You're right. It can.

This guide shows you how, one small honest step at a time.

## What you'll learn

- **Why pasting fails at scale** ([Chapter 1](01-why-pasting-fails.md)) — and
  why you shouldn't feel bad about it. Everyone hits this wall.
- **Simple retrieval ideas** ([Chapter 2](02-simple-retrieval.md)) — plain
  search, tagging, and outlines: the underrated 80% wins.
- **A tiny quote-file RAG** ([Chapter 3](03-quote-file-rag.md)) — a working
  tool you build step by step, powered by [Ollama](https://ollama.com) on your
  own machine (with a fully-offline fallback built in).
- **The folder-packing approach** ([Chapter 4](04-folder-packing.md)) — one
  prompt that carries your whole folder.
- **Privacy rules** ([Chapter 5](05-privacy-rules.md)) — how to keep personal
  files personal.
- **When answers deserve doubt** ([Chapter 6](06-when-to-doubt.md)) — the
  healthiest skill in this whole manual.
- **A guided first project** ([Chapter 7](07-first-project.md)) — from empty
  folder to first real answer, in one sitting.
- **A session checklist** ([Chapter 8](08-checklist.md)) — a pocket version of
  everything important.
- **A glossary** ([Chapter 9](09-glossary.md)) — every term in this book,
  explained like a friend would.

## How to read it

- If you're brand new, read Chapters 1 and 2 first. They change how you think,
  and they require zero tools.
- If you want to *do* something today, go straight to Chapter 7 (the first
  project); it will send you back to earlier chapters exactly when you need them.
- Every chapter ends with **In one sentence** — a plain-English takeaway you can
  hold in your head all day.

## A promise about scope

Nothing in this guide is medical, legal, or financial advice. When we use
examples like insurance letters and medical bills, we're teaching *document
skills*, not professional judgment. Chapter 6 says more about where an AI
helper's confidence is earned and where it isn't.

## One line per chapter, big picture

> **Don't paste the library. Bring the page.**

Everything after this sentence is just careful ways of doing that.

*Companion tools mentioned in this guide:* **folder-to-prompt-cli**
(Chapter 4) and **chat-export-archiver-cli** (turning your old chat exports into
a searchable archive). This site was built from Markdown with a simple local
build script — `python3 tools/build_site.py` — so you can rebuild the whole book
yourself.
