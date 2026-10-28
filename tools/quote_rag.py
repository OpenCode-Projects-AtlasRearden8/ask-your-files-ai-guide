#!/usr/bin/env python3
"""quote_rag.py — a tiny "quote-file" RAG for your own documents, fully local.

Chops .txt/.md files in a folder into paragraph-sized quotes, stores them in a
plain JSON index, and scores the quotes against your question to surface the
few that answer it — like Chapter 3 of the Ask Your Files AI Guide.

Works completely offline using a built-in TF-IDF scorer. If Ollama
(https://ollama.com) is installed and running, you can rebuild the index with
local embeddings for meanin-based ranking, and optionally have a local model
draft an answer from the top quotes (--answer).

Usage:
  quote_rag.py build ./my-docs --store quotes.json [--embed nomic-embed-text]
  quote_rag.py ask   quotes.json "my question" [--top 5] [--answer] [--model llama3.2]
  quote_rag.py peek  quotes.json

No network access is required or used, except optional HTTP calls to a local
Ollama server at 127.0.0.1:11434 (never to the internet).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

TEXT_EXTS = {".txt", ".md"}
OLLAMA_URL = "http://127.0.0.1:11434"
INDEX_VERSION = 1

_STOPWORDS = frozenset(
    """a about above after again all am an and any are as at be because been
    before being below between both but by can did do does doing down during
    each few for from further had has have having he her here hers him his how
    i if in into is it its just me more most my no nor not of off on once only
    or other our out over own same she should so some such than that the their
    them then there these they this those through to too under until up very
    was we were what when where which while who whom why will with you your""".split()
)

_WORD_RE = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return [w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS and len(w) > 1]


def split_into_quotes(text: str, max_len: int = 900) -> list[dict]:
    """Split a file's text into paragraph-sized quotes, keeping headings."""
    quotes: list[dict] = []
    current_head: str | None = None
    blocks = re.split(r"\n\s*\n", text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        head = current_head
        if block.startswith("#"):
            m = re.match(r"^(#{1,6})\s+(.*)$", block, flags=re.S)
            if m:
                first_line = block.splitlines()[0]
                hh = re.match(r"^(#{1,6})\s+(.*)$", first_line)
                if hh:
                    current_head = hh.group(2).strip()
                    head = current_head
                    remainder = block[len(first_line):].strip()
                    if remainder:
                        quotes.append(_mk(remainder, head))
                    else:
                        continue
            else:
                pass
        if block.startswith(">"):
            block = re.sub(r"^>\s?", "", block, flags=re.M).strip()
            if not block:
                continue
        if not head:
            first = block.splitlines()[0]
            if re.match(r"#{1,6}\s", first):
                head = re.sub(r"^#{1,6}\s+", "", first).strip()
        if len(block) > max_len:
            # Split over-long blocks at sentence boundaries so every quote stays quotable.
            for piece in wrap_sentences(block, max_len):
                quotes.append(_mk(piece, head))
        else:
            quotes.append(_mk(block, head))
    return quotes


def _mk(text: str, head: str | None) -> dict:
    return {"text": text, "head": head}


def wrap_sentences(text: str, max_len: int) -> list[str]:
    out: list[str] = []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    cur = ""
    for s in sentences:
        if cur and len(cur) + 1 + len(s) > max_len:
            out.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        out.append(cur)
    return out or [text[:max_len]]


def ollama_embed(text: str, model: str) -> list[float] | None:
    """Ask a local Ollama server for embeddings; None if unavailable."""
    try:
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/embeddings",
            data=json.dumps({"model": model, "prompt": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        vec = data.get("embedding")
        if isinstance(vec, list) and vec:
            return vec
    except Exception:
        return None
    return None


def tfidf_from_corpus(docs: list[list[str]]) -> tuple[dict[str, float], dict[str, float]]:
    df = Counter()
    for toks in docs:
        for term in set(toks):
            df[term] += 1
    n = len(docs)
    idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}
    return df, idf


def cosine(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    common = set(vec_a) & set(vec_b)
    num = sum(vec_a[t] * vec_b[t] for t in common)
    na = math.sqrt(sum(v * v for v in vec_a.values()))
    nb = math.sqrt(sum(v * v for v in vec_b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


def build_index(folder: Path, embed_model: str | None) -> dict:
    quotes: list[dict] = []
    files = sorted(
        p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_EXTS
    )
    for fp in files:
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"  ! skipping {fp.name}: {e}", file=sys.stderr)
            continue
        rel = fp.relative_to(folder).as_posix()
        for q in split_into_quotes(text):
            quotes.append({"file": rel, **q})

    embedding_mode = "tfidf"
    if embed_model:
        ok = True
        for q in quotes:
            vec = ollama_embed(q["text"], embed_model)
            if vec is None:
                ok = False
                print("  ! Ollama not reachable; falling back to TF-IDF.", file=sys.stderr)
                break
            q["vec"] = vec
        if ok and quotes:
            embedding_mode = f"ollama:{embed_model}"
        else:
            for q in quotes:
                q.pop("vec", None)

    # TF vectors + IDF are always stored, so ask() can fall back gracefully.
    toks = [tokenize(q["text"]) for q in quotes]
    _, idf = tfidf_from_corpus(toks)
    for q, qs_toks in zip(quotes, toks):
        counts = Counter(qs_toks)
        tfvec = {t: counts[t] * idf.get(t, 0.0) for t in counts}
        q["tf"] = {t: round(v, 6) for t, v in tfvec.items() if v > 0}

    index = {
        "version": INDEX_VERSION,
        "source": folder.as_posix(),
        "embedding": embedding_mode,
        "idf": {k: round(v, 6) for k, v in sorted(idf.items())},
        "quotes": quotes,
    }
    return index


def new_store_embeddings_enabled(index: dict) -> bool:
    return str(index.get("embedding", "tfidf")).startswith("ollama:")


def norm_tfidf_vec(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokenize(text))
    return {t: counts[t] * idf.get(t, 1.0) for t in counts}


def ask(index: dict, question: str, top: int) -> list[dict]:
    """Return up to `top` quotes scored against the question, best first."""
    quotes = index.get("quotes", [])
    if new_store_embeddings_enabled(index):
        model = str(index["embedding"]).split(":", 1)[1]
        qvec = ollama_embed(question, model)
        if qvec is not None:
            scored = [
                {
                    "score": cosine({i: v for i, v in enumerate(qvec)},
                                    {i: v for i, v in enumerate(q.get("vec", []))}),
                    "quote": q,
                }
                for q in quotes
            ]
            scored.sort(key=lambda s: s["score"], reverse=True)
            return scored[:top]

    # TF-IDF fallback (also used when Ollama is unreachable).
    idf = index.get("idf", {})
    qvec = norm_tfidf_vec(question, idf)
    scored = [
        {
            "score": cosine(qvec, q.get("tf", {})),
            "quote": q,
        }
        for q in quotes
    ]
    scored.sort(key=lambda s: s["score"], reverse=True)
    return scored[:top]


def collect_sources(scored: list[dict], max_total: int = 4000) -> list[dict]:
    """Pick quotes for an --answer prompt, under a total-character budget."""
    picked: list[dict] = []
    used = 0
    for item in scored:
        text = item["quote"]["text"]
        if used + len(text) > max_total:
            break
        picked.append(item)
        used += len(text)
    return picked


def build_answer_prompt(question: str, picked: list[dict]) -> str:
    lines = [
        "Answer ONLY using the quotes below. If they don't contain the answer, "
        "say exactly: \"The quotes don't contain that.\"",
        "",
        f"Question: {question}",
        "",
    ]
    for item in picked:
        q = item["quote"]
        source = f"{q.get('file', '?')}" + (f" (Section: {q['head']})" if q.get("head") else "")
        lines.append(f"Quote from {source}:")
        lines.append(q["text"])
        lines.append("")
    return "\n".join(lines)


def ollama_answer(prompt: str, model: str, temperature: float = 0.0) -> str | None:
    try:
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=json.dumps({"model": model, "prompt": prompt,
                             "stream": False, "options": {"temperature": temperature}}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.load(resp)
        return data.get("response")
    except Exception as e:
        print(f"  ! Couldn't get an answer from the local model ({e}).",
              file=sys.stderr)
        return None


def peek_index(index: dict) -> str:
    quotes = index.get("quotes", [])
    files = sorted({q.get("file", "?") for q in quotes})
    lines = [
        f"embedding mode: {index.get('embedding')}",
        f"quotes: {len(quotes)}",
        "files:",
    ]
    lines += [f"  - {f}" for f in files]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="quote_rag", description="A tiny local quote-file RAG.",
        epilog=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a quote-file index from a folder")
    b.add_argument("folder", type=Path)
    b.add_argument("--store", required=True, type=Path, help="output JSON index path")
    b.add_argument("--embed", default=None, metavar="MODEL",
                   help="use this Ollama embedding model (e.g. nomic-embed-text)")

    a = sub.add_parser("ask", help="score the index's quotes against a question")
    a.add_argument("store", type=Path)
    a.add_argument("question")
    a.add_argument("--top", type=int, default=5)
    a.add_argument("--answer", action="store_true",
                   help="also draft an answer with a local Ollama chat model")
    a.add_argument("--model", default="llama3.2", metavar="MODEL",
                   help="local chat model for --answer (default: llama3.2)")

    p = sub.add_parser("peek", help="summarize an index")
    p.add_argument("store", type=Path)

    ns = ap.parse_args(argv)

    if ns.cmd == "build":
        if not ns.folder.is_dir():
            print(f"Not a folder: {ns.folder}", file=sys.stderr)
            return 2
        t0 = time.time()
        index = build_index(ns.folder, ns.embed)
        ns.store.parent.mkdir(parents=True, exist_ok=True)
        ns.store.write_text(
            json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        dt = time.time() - t0
        n_files = len({q["file"] for q in index["quotes"]})
        mode = index["embedding"]
        print(f"Indexed {len(index['quotes'])} quotes from {n_files} file(s) "
              f"({mode}) -> {ns.store} [{dt:.2f}s]")
        return 0

    if ns.cmd == "peek":
        index = json.loads(ns.store.read_text(encoding="utf-8"))
        print(peek_index(index))
        return 0

    if ns.cmd == "ask":
        if not ns.store.is_file():
            print(f"Index not found: {ns.store} (run `quote_rag.py build` first)",
                  file=sys.stderr)
            return 2
        index = json.loads(ns.store.read_text(encoding="utf-8"))
        t0 = time.time()
        scored = ask(index, ns.question, max(1, ns.top))
        dt = time.time() - t0
        if not scored:
            print("No quotes in this index. Rebuild it first.", file=sys.stderr)
            return 1
        best = scored[0]["score"]
        floor = 0.05 if new_store_embeddings_enabled(index) else 0.03
        hits = [s for s in scored if s["score"] >= floor] or (
            scored[:1] if best > 0 else []
        )
        if best <= 0:
            print(f"Top quotes for: {ns.question!r}  (searched in {dt * 1000:.0f} ms)")
            print("\nNo quotes matched. Try words the documents themselves use, "
                  "or rebuild the index.")
            return 1
        print(f"Top quotes for: {ns.question!r}  (searched in {dt * 1000:.0f} ms)")
        for item in hits:
            q = item["quote"]
            loc = q.get("file", "?")
            if q.get("head"):
                loc += f" — {q['head']}"
            print(f"\n[{item['score']:.2f}] {loc}:")
            print(f"  {q['text']}")

        if ns.answer:
            picked = collect_sources(scored)
            if not picked:
                print("\nNo usable quotes to answer with.", file=sys.stderr)
                return 1
            prompt = build_answer_prompt(ns.question, picked)
            print(f"\nAsking local model '{ns.model}' with {len(picked)} quote(s)...")
            answer = ollama_answer(prompt, ns.model)
            if answer is None:
                return 1
            print("\n--- Answer (from local model, using only the quotes) ---")
            print(answer.strip())
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
