#!/usr/bin/env python3
"""
build_review_package.py — emit a self-contained review document per book.

    python3 tools/build_review_package.py            # all indexed books
    python3 tools/build_review_package.py john       # one book

Writes index/reviews/<book>-package.md.

Why this exists. The index files carry references, not scripture; the text lives
separately in index/text/. A reviewer handed only the index file is judging every
connection from a reference and the drafter's own summary of the passage — that is,
from recall rather than from the text. Across the first four books, every flag a
reviewer raised concerned a practice definition and none concerned a misreading,
which is what you would expect from a reviewer who could check the tags but not the
passages.

This document puts the passage and the claim side by side, so a reviewer can check
whether a connection survives contact with what the verses actually say.

Scripture is the World English Bible, which is in the public domain.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index"
TEXT = INDEX / "text"
OUT = INDEX / "reviews"

REF_RE = re.compile(r"^(.+?)\s+(\d+):(\d+)(?:[-–](\d+))?$")

MODE_GLOSS = {
    "prescribes": "the passage commands this practice",
    "exemplifies": "someone in the passage does it",
    "counter-example": "the passage shows what its absence costs",
}


def verses_for(text_data, ref):
    m = REF_RE.match(ref)
    if not m:
        return []
    ch, lo = int(m.group(2)), int(m.group(3))
    hi = int(m.group(4) or lo)
    out = []
    for v in range(lo, hi + 1):
        body = text_data["verses"].get(f"{ch}:{v}")
        if body:
            out.append((f"{ch}:{v}", body))
    return out


def build_book(slug):
    idx_path = INDEX / f"{slug}.json"
    txt_path = TEXT / f"{slug}.json"
    if not idx_path.exists() or not txt_path.exists():
        print(f"  ! {slug}: missing index or text file — skipped")
        return None
    d = json.loads(idx_path.read_text(encoding="utf-8"))
    t = json.loads(txt_path.read_text(encoding="utf-8"))
    book = d["book"]

    L = []
    a = L.append
    a(f"# {book} — review package")
    a("")
    a(f"Scripture: World English Bible (public domain). "
      f"Index status: {d.get('status', 'complete')}. "
      f"Method version {d.get('method_version', '?')}.")
    a("")
    a("Every entry below shows the passage in full, then the claim made about it. "
      "Read the passage before the claim. The question is not whether the tags are "
      "internally consistent — it is whether they survive contact with the text.")
    a("")
    for key, label in (("note", "Note"), ("genre_note", "Genre note"),
                       ("structural_note", "Structural note"),
                       ("prediction_note", "Prediction note"),
                       ("schema_note", "Schema note"),
                       ("synoptic_note", "Synoptic note"),
                       ("interpretive_note", "Interpretive note"),
                       ("coverage_note", "Coverage note"),
                       ("method_rule", "Method rule")):
        if d.get(key):
            a(f"**{label}.** {d[key]}")
            a("")
    a("---")
    a("")

    for i, e in enumerate(d["entries"], 1):
        a(f"## {i}. {e['ref']} — {e['pericope']}")
        a("")

        refs = e["refs"] if e.get("kind") == "cluster" else [e["ref"]]
        if e.get("kind") == "cluster":
            a(f"*Thematic cluster — {len(refs)} passages gathered from across the book.*")
            a("")
        for r in refs:
            for vref, body in verses_for(t, r):
                a(f"> **{vref}** {body}")
        a("")

        if e.get("synoptic_parallel"):
            a(f"*Also in Luke: {e['synoptic_parallel']}*")
            a("")
        a(f"**Claim.** {e['connection']}")
        a("")

        bits = [
            f"pillars: {', '.join(e['pillars']) or '—'}",
            f"stages: {', '.join(e['stages']) or '—'}",
            f"chapters: {', '.join(e['chapters']) or '—'}",
            f"practices: {', '.join(e['practices']) or 'none'}",
            f"confidence: {e['confidence']}",
        ]
        if e.get("mode"):
            bits.insert(0, f"mode: {e['mode']} ({MODE_GLOSS[e['mode']]})")
        a("**Tags.** " + " · ".join(bits))
        a("")

        flags = []
        if e.get("prior"):
            flags.append("**Prior** — cited in the curriculum before this index existed. "
                         "The author's judgment, not the drafter's.")
        if e.get("author_corrected"):
            flags.append("**Author placed** — settled by the author. Note disagreement if you "
                         "have it, but do not propose a change.")
        if e.get("review"):
            flags.append(f"**Amended at review** — {e['review']}")
        for f in flags:
            a(f)
            a("")
        a("---")
        a("")

    doc = "\n".join(L) + "\n"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}-package.md").write_text(doc, encoding="utf-8")
    words = len(doc.split())
    print(f"  {slug}-package.md — {len(d['entries'])} entries, {words:,} words")
    return words


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1:
        slugs = sys.argv[1:]
    else:
        slugs = sorted(p.stem for p in INDEX.glob("*.json"))
    total = 0
    for s in slugs:
        w = build_book(s)
        if w:
            total += w
    print(f"Review packages written to index/reviews/ — {total:,} words total")


if __name__ == "__main__":
    main()
