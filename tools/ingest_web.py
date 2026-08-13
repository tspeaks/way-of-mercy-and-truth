#!/usr/bin/env python3
"""
ingest_web.py — split the full World English Bible into per-book text files.

    python3 tools/ingest_web.py path/to/full.txt

Reads the plain-text WEB distribution (one verse per line, "Book C:V<TAB>text")
and writes index/text/<book-slug>.json for every book found.

Run this once. After it, indexing a new book needs no network access at all —
the text is already local, and build_scripture.py will find it.

The World English Bible is in the public domain. Its translators dedicated it so
that work like this could be built on it and given away again, which is exactly
what happens here.
"""

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "index" / "text"

LINE_RE = re.compile(r"^((?:[123]\s)?[A-Z][A-Za-z'\-]*(?:\s(?:of\s)?[A-Z][A-Za-z'\-]*)*)\s+(\d+):(\d+)\t(.*)$")

# Canonical order, so the site can present books in the order a reader expects
# rather than the order the source file happens to use.
CANON = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges",
    "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles",
    "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
    "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
    "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus",
    "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John",
    "3 John", "Jude", "Revelation",
]

NOTE = ("Public domain. Dedicated to the public domain by its translators, who permit "
        "copying, publication, redistribution, quotation, and reproduction without "
        "restriction, asking only that altered text not carry the World English Bible name.")

# Different WEB distributions title a few books slightly differently.
ALIASES = {
    "Psalm": "Psalms",
    "Song of Songs": "Song of Solomon",
    "Canticles": "Song of Solomon",
    "Revelation of John": "Revelation",
}


def slug(book):
    return book.lower().replace(" ", "-")


def ingest(src):
    books = OrderedDict()
    skipped = 0
    for line in Path(src).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        m = LINE_RE.match(line)
        if not m:
            skipped += 1
            continue
        book, ch, v, text = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4).strip()
        book = ALIASES.get(book, book)
        books.setdefault(book, {})[f"{ch}:{v}"] = text

    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    total_v = 0
    unknown = []

    for book in sorted(books, key=lambda b: CANON.index(b) if b in CANON else 999):
        verses = books[book]
        if book not in CANON:
            unknown.append(book)
        chapters = max(int(k.split(":")[0]) for k in verses)
        payload = {
            "book": book,
            "canonical_order": CANON.index(book) + 1 if book in CANON else None,
            "translation": "World English Bible",
            "translation_note": NOTE,
            "source": "worldenglish.bible",
            "chapters": chapters,
            "verses": dict(sorted(
                verses.items(),
                key=lambda kv: (int(kv[0].split(":")[0]), int(kv[0].split(":")[1])))),
        }
        (OUT / f"{slug(book)}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written += 1
        total_v += len(verses)

    print(f"{written} books  ·  {total_v:,} verses  ->  index/text/")
    missing = [b for b in CANON if b not in books]
    if missing:
        print(f"  not found in source: {missing}")
    if unknown:
        print(f"  present but not in canon list: {unknown}")
    if skipped:
        print(f"  {skipped} unparsed line(s) — header/footer text, normally fine")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(ingest(sys.argv[1]))
