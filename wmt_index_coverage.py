#!/usr/bin/env python3
"""
wmt_index_coverage.py — coverage report + chapter-keyed regrouping
for the Way of Mercy and Truth scripture index.

Run it from the root of the repo:

    python3 wmt_index_coverage.py

It does two things:

  1. Prints a coverage report — how many indexed passages land on each
     chapter (C01-C29) and each practice (PR01-PR30), sorted heaviest
     first, plus which books feed each one.

  2. Writes by-chapter.json — the same entries regrouped under their
     chapter and practice tags instead of under their source book.
     That is the file a devotional generator reads.

Standard library only. No install, no network.

If the counts come out zero or obviously wrong, run:

    python3 wmt_index_coverage.py --debug

which prints a sample of what it actually found in the markup, so you
can see where the parse is going astray.
"""

import argparse
import glob
import html
import json
import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------
# Locating the data
# ---------------------------------------------------------------------

# Preferred: structured JSON under index/. If your entries live there in
# some form, parsing that is more reliable than parsing rendered HTML.
JSON_GLOBS = ["index/*.json", "index/**/*.json"]

# Fallback: the rendered per-book pages at the repo root.
HTML_GLOB = "scripture-*.html"

CHAPTER_RE = re.compile(r"\bC([0-2][0-9])\b")
PRACTICE_RE = re.compile(r"\bPR([0-3][0-9])\b")

# An entry block in the rendered pages. Entries are <div class="entry">
# ... </div> containing a .entry-ref, an .entry-name, and a .tags block.
ENTRY_RE = re.compile(
    r'<(?:div|article|section)[^>]*class="[^"]*\bentry\b[^"]*"[^>]*>(.*?)'
    r'(?=<(?:div|article|section)[^>]*class="[^"]*\bentry\b|</main>|</body>)',
    re.DOTALL | re.IGNORECASE,
)

REF_RE = re.compile(
    r'class="[^"]*\bentry-ref\b[^"]*"[^>]*>(.*?)<', re.DOTALL | re.IGNORECASE
)
NAME_RE = re.compile(
    r'class="[^"]*\bentry-name\b[^"]*"[^>]*>(.*?)<', re.DOTALL | re.IGNORECASE
)
TAGS_BLOCK_RE = re.compile(
    r'<div[^>]*class="[^"]*\btags\b[^"]*"[^>]*>(.*?)</div>', re.DOTALL | re.IGNORECASE
)
TAG_RE = re.compile(
    r'<(?:a|span)[^>]*class="([^"]*\btag\b[^"]*)"[^>]*>(.*?)</(?:a|span)>',
    re.DOTALL | re.IGNORECASE,
)
STRIP_TAGS_RE = re.compile(r"<[^>]+>")


def clean(fragment):
    """Turn a chunk of markup into plain readable text."""
    return html.unescape(STRIP_TAGS_RE.sub(" ", fragment or "")).strip()


def book_from_filename(path):
    stem = os.path.basename(path)
    stem = re.sub(r"^scripture-", "", stem)
    stem = re.sub(r"\.html$", "", stem)
    return stem.replace("-", " ").title()


# ---------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------


def parse_html_file(path, debug=False):
    """Pull entries out of one rendered scripture-*.html page."""
    with open(path, "r", encoding="utf-8") as fh:
        markup = fh.read()

    book = book_from_filename(path)
    entries = []

    for block in ENTRY_RE.findall(markup):
        ref_match = REF_RE.search(block)
        name_match = NAME_RE.search(block)
        tags_match = TAGS_BLOCK_RE.search(block)

        # Read tags from the .tags block when present; fall back to the
        # whole entry so a markup variation does not silently drop it.
        tag_source = tags_match.group(1) if tags_match else block

        raw_tags = []
        for css_class, label in TAG_RE.findall(tag_source):
            raw_tags.append({"classes": css_class.strip(), "label": clean(label)})

        tag_text = " ".join(t["label"] for t in raw_tags)
        if not tag_text.strip():
            tag_text = clean(tag_source)

        chapters = sorted({"C" + n for n in CHAPTER_RE.findall(tag_text)})
        practices = sorted({"PR" + n for n in PRACTICE_RE.findall(tag_text)})

        if not chapters and not practices:
            if debug:
                print(f"  [no tags found] {book}: {clean(block)[:90]}", file=sys.stderr)
            continue

        entries.append(
            {
                "book": book,
                "reference": clean(ref_match.group(1)) if ref_match else "",
                "name": clean(name_match.group(1)) if name_match else "",
                "chapters": chapters,
                "practices": practices,
                "tags": [t["label"] for t in raw_tags],
                "source_file": os.path.basename(path),
            }
        )

    return entries


def parse_json_file(path):
    """Best-effort read of structured entries under index/."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []

    # Find the list of entry-like dicts, wherever it sits in the file.
    candidates = []
    if isinstance(data, list):
        candidates = data
    elif isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                candidates = value
                break

    book = book_from_filename(path)
    entries = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        blob = json.dumps(item)
        chapters = sorted({"C" + n for n in CHAPTER_RE.findall(blob)})
        practices = sorted({"PR" + n for n in PRACTICE_RE.findall(blob)})
        if not chapters and not practices:
            continue
        entries.append(
            {
                "book": item.get("book", book),
                "reference": str(item.get("reference") or item.get("ref") or ""),
                "name": str(item.get("name") or item.get("title") or ""),
                "chapters": chapters,
                "practices": practices,
                "tags": [],
                "source_file": os.path.basename(path),
            }
        )
    return entries


def collect(debug=False):
    entries = []
    used = []

    json_paths = []
    for pattern in JSON_GLOBS:
        json_paths.extend(glob.glob(pattern, recursive=True))
    # index/text/ holds the raw WEB Bible, not index entries — skip it.
    json_paths = [p for p in sorted(set(json_paths)) if "/text/" not in p.replace("\\", "/")]

    for path in json_paths:
        found = parse_json_file(path)
        if found:
            entries.extend(found)
            used.append(path)

    if not entries:
        for path in sorted(glob.glob(HTML_GLOB)):
            found = parse_html_file(path, debug=debug)
            if found:
                entries.extend(found)
                used.append(path)

    return entries, used


# ---------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------


def report(entries):
    by_chapter = defaultdict(list)
    by_practice = defaultdict(list)

    for entry in entries:
        for chapter in entry["chapters"]:
            by_chapter[chapter].append(entry)
        for practice in entry["practices"]:
            by_practice[practice].append(entry)

    def block(title, mapping, universe):
        print(f"\n{title}")
        print("-" * len(title))
        ranked = sorted(mapping.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        for key, items in ranked:
            books = sorted({i["book"] for i in items})
            shown = ", ".join(books[:5])
            if len(books) > 5:
                shown += f", +{len(books) - 5} more"
            print(f"  {key}  {len(items):>4} passages   {shown}")
        empty = [k for k in universe if k not in mapping]
        if empty:
            print(f"\n  No coverage yet: {', '.join(empty)}")

    all_chapters = [f"C{n:02d}" for n in range(1, 30)]
    all_practices = [f"PR{n:02d}" for n in range(1, 31)]

    print(f"\nParsed {len(entries)} tagged entries "
          f"across {len({e['book'] for e in entries})} books.")
    block("Coverage by chapter", by_chapter, all_chapters)
    block("Coverage by practice", by_practice, all_practices)

    if by_chapter:
        best = max(by_chapter.items(), key=lambda kv: len(kv[1]))
        print(f"\nBest-covered chapter: {best[0]} ({len(best[1])} passages)")

    return by_chapter, by_practice


def write_grouped(by_chapter, by_practice, out_path="by-chapter.json"):
    payload = {
        "chapters": {
            key: sorted(items, key=lambda e: (e["book"], e["reference"]))
            for key, items in sorted(by_chapter.items())
        },
        "practices": {
            key: sorted(items, key=lambda e: (e["book"], e["reference"]))
            for key, items in sorted(by_practice.items())
        },
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"\nWrote {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debug", action="store_true",
                        help="print entries where no C/PR tag was found")
    parser.add_argument("--out", default="by-chapter.json",
                        help="output path for the regrouped entries")
    args = parser.parse_args()

    entries, used = collect(debug=args.debug)

    if not entries:
        print("No tagged entries found.", file=sys.stderr)
        print("Check that you are running this from the repo root, and try "
              "--debug to see what the parser is actually reading.",
              file=sys.stderr)
        return 1

    print("Read from:")
    for path in used:
        print(f"  {path}")

    by_chapter, by_practice = report(entries)
    write_grouped(by_chapter, by_practice, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
