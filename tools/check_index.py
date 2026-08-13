#!/usr/bin/env python3
"""
check_index.py — validate a scripture index file against the curriculum.

    python3 tools/check_index.py index/james.json

Catches the errors that are easy to make by hand and impossible to see by eye:
tags that point at stages, chapters, or practices that do not exist; verse ranges
that overlap or leave gaps; entries missing required fields.

It also reports coverage — which practices and chapters the book anchors and which
it does not. Absence is information, not failure. A book that anchors everything is
more likely to be badly indexed than unusually rich.

Exits non-zero if anything is structurally wrong, so it can gate a commit.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STAGES = {f"S{i}" for i in range(1, 8)}
CHAPTERS = {f"C{i:02d}" for i in range(1, 30)}
PRACTICES = {f"PR{i:02d}" for i in range(1, 31)}
PILLARS = {"truth", "mercy", "humility"}
CONFIDENCE = {"high", "medium", "low"}
# Narrative books need to say whether a passage commands a practice, shows it done,
# or shows what its absence costs. Optional: didactic books often need no mode.
MODES = {"prescribes", "exemplifies", "counter-example"}
REQUIRED = ["ref", "pericope", "pillars", "stages", "chapters",
            "practices", "connection", "confidence", "prior"]

def verse_counts(book):
    """Chapter->verse-count for a book, read from its ingested text file."""
    p = ROOT / "index" / "text" / f"{book.lower().replace(' ', '-')}.json"
    if not p.exists():
        return None
    verses = json.loads(p.read_text(encoding="utf-8"))["verses"]
    out = {}
    for k in verses:
        c, v = (int(x) for x in k.split(":"))
        out[c] = max(out.get(c, 0), v)
    return dict(sorted(out.items()))

# Book names may be multi-word ("Song of Solomon") or numbered ("1 Corinthians").
REF_RE = re.compile(r"^(.+?)\s+(\d+):(\d+)(?:[-–](\d+))?$")


def check(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    book = data.get("book", "?")
    entries = data.get("entries", [])
    errors, warnings = [], []

    print(f"{book} — {len(entries)} entries, method v{data.get('method_version','?')}")

    covered = {}
    for i, e in enumerate(entries):
        where = e.get("ref", f"entry {i}")

        for f in REQUIRED:
            if f not in e:
                errors.append(f"{where}: missing field '{f}'")

        for field, valid in (("stages", STAGES), ("chapters", CHAPTERS),
                             ("practices", PRACTICES), ("pillars", PILLARS)):
            for v in e.get(field, []):
                if v not in valid:
                    errors.append(f"{where}: invalid {field[:-1]} '{v}'")

        if "mode" in e and e["mode"] not in MODES:
            errors.append(f"{where}: mode must be one of {sorted(MODES)}")

        if e.get("confidence") not in CONFIDENCE:
            errors.append(f"{where}: confidence must be one of {sorted(CONFIDENCE)}")

        if not e.get("pillars"):
            warnings.append(f"{where}: no pillar assigned")
        if not e.get("stages"):
            warnings.append(f"{where}: no stage assigned")

        conn = e.get("connection", "")
        if len(conn.split()) < 12:
            warnings.append(f"{where}: connection is thin ({len(conn.split())} words)")

        if e.get("kind") == "cluster":
            if not e.get("refs"):
                errors.append(f"{where}: cluster entry has no refs array")
            for r in e.get("refs", []):
                if not REF_RE.match(r):
                    errors.append(f"{where}: unparseable ref in cluster — {r}")
            continue

        m = REF_RE.match(e.get("ref", ""))
        if not m:
            errors.append(f"{where}: unparseable reference")
            continue
        ch, lo = int(m.group(3) and m.group(2)), int(m.group(3))
        hi = int(m.group(4) or lo)
        if hi < lo:
            errors.append(f"{where}: reversed verse range")
        for v in range(lo, hi + 1):
            covered.setdefault(ch, set()).add(v)
            if sum(1 for x in entries
                   if x.get("ref", "").startswith(f"{book} {ch}:")) and False:
                pass

    # overlap detection
    seen = {}
    clustered = set()
    for e in entries:
        if e.get("kind") == "cluster":
            for r in e.get("refs", []):
                mm = REF_RE.match(r)
                if mm:
                    clustered.add((int(mm.group(2)), int(mm.group(3))))
            continue
        m = REF_RE.match(e.get("ref", ""))
        if not m:
            continue
        ch, lo = int(m.group(2)), int(m.group(3))
        hi = int(m.group(4) or lo)
        for v in range(lo, hi + 1):
            if (ch, v) in seen:
                warnings.append(f"{e['ref']}: verse {ch}:{v} also in {seen[(ch, v)]}")
            seen[(ch, v)] = e["ref"]

    # coverage
    vc = verse_counts(book)
    if vc:
        print("\nverse coverage")
        total_have = total_want = 0
        for ch, want in sorted(vc.items()):
            have = len({v for (c, v) in seen if c == ch})
            total_have += have
            total_want += want
            gaps = sorted(set(range(1, want + 1)) - {v for (c, v) in seen if c == ch})
            if have == 0:
                print(f"  ch{ch}: not indexed")
                continue
            if gaps:
                shown = ", ".join(str(g) for g in gaps[:12])
                more = f" (+{len(gaps)-12} more)" if len(gaps) > 12 else ""
                gap_s = f"  uncovered: {shown}{more}"
            else:
                gap_s = ""
            print(f"  ch{ch}: {have}/{want}{gap_s}")
        print(f"  total: {total_have}/{total_want} in pericopes")
        if clustered:
            print(f"  {len(clustered)} further verse(s) gathered thematically into clusters")

    print("\ndistribution")
    kinds = Counter(e.get("kind", "pericope") for e in entries)
    if len(kinds) > 1:
        print("  entry kind:", dict(kinds))
    print("  confidence:", dict(Counter(e.get("confidence") for e in entries)))
    if any("mode" in e for e in entries):
        print("  mode:      ", dict(Counter(e.get("mode","-") for e in entries)))
    print("  pillars:   ", dict(Counter(p for e in entries for p in e.get("pillars", []))))
    print("  stages:    ", dict(sorted(Counter(
        s for e in entries for s in e.get("stages", [])).items())))

    pc = Counter(p for e in entries for p in e.get("practices", []))
    cc = Counter(c for e in entries for c in e.get("chapters", []))
    print(f"\nanchors")
    print(f"  practices: {len(pc)}/30   unanchored: {sorted(PRACTICES - set(pc))}")
    print(f"  chapters:  {len(cc)}/29   unanchored: {sorted(CHAPTERS - set(cc))}")

    if warnings:
        print(f"\nwarnings ({len(warnings)})")
        for w in warnings[:15]:
            print("  ·", w)
        if len(warnings) > 15:
            print(f"  … {len(warnings)-15} more")

    if errors:
        print(f"\nERRORS ({len(errors)})")
        for e in errors:
            print("  ✗", e)
        return 1

    print("\nstructurally valid.")
    return 0


if __name__ == "__main__":
    paths = sys.argv[1:] or [str(ROOT / "index" / "james.json")]
    sys.exit(max(check(p) for p in paths))
