#!/usr/bin/env python3
"""
Build machine-readable artifacts for The Way of Mercy and Truth.

Generates:
  llms.txt          - index for language models and humans
  manifest.json     - structured index
  dist/wmt-full.txt - whole curriculum as one plain-text file
  dist/*.txt        - per-section plain text

Run: python3 tools/build.py
"""
import json, os, re, sys, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRUNK = ROOT / "trunk"
DIST = ROOT / "dist"

ORDER_KEY = {"front-matter": 0, "stage": 1, "chapter": 2, "appendix": 3}

def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None
    meta_raw, body = m.groups()
    meta = {}
    for line in meta_raw.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    meta["body"] = body.strip()
    meta["path"] = str(path.relative_to(ROOT))
    return meta

def sort_key(s):
    sid = s["id"]
    num = re.search(r"(\d+)", sid)
    n = int(num.group(1)) if num else 0
    if sid.startswith("WMT P"): return (0, 0)
    if sid.startswith("WMT G"): return (4, n)
    if sid.startswith("WMT S"): return (1, n)
    if sid.startswith("WMT C"): return (2, n)
    return (3, n)

def main():
    sections = []
    for p in sorted(TRUNK.rglob("*.md")):
        if p.name == "front-matter.md":
            continue
        s = parse(p)
        if s:
            sections.append(s)
    sections.sort(key=sort_key)

    genealogy = []
    GEN = ROOT / "genealogy"
    if GEN.exists():
        for p in sorted(GEN.rglob("*.md")):
            s = parse(p)
            if s:
                genealogy.append(s)
        genealogy.sort(key=lambda x: x["id"])

    DIST.mkdir(exist_ok=True)
    version = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else "0.0.0"

    # per-section plain text
    for s in sections:
        plain = re.sub(r"^#+ ", "", s["body"], flags=re.M)
        plain = re.sub(r"\*(.+?)\*", r"\1", plain)
        out = DIST / f"{Path(s['path']).stem}.txt"
        out.write_text(plain + "\n", encoding="utf-8")
        s["txt"] = f"dist/{out.name}"
        s["words"] = len(plain.split())

    for s in genealogy:
        plain = re.sub(r"^#+ ", "", s["body"], flags=re.M)
        plain = re.sub(r"\*(.+?)\*", r"\1", plain)
        out = DIST / f"genealogy-{Path(s['path']).stem}.txt"
        out.write_text(plain + "\n", encoding="utf-8")
        s["txt"] = f"dist/{out.name}"
        s["words"] = len(plain.split())

    # full corpus
    full = []
    for s in sections:
        full.append(f"=== {s['id']} — {s['title']} ===\n")
        full.append(re.sub(r"^#+ ", "", s["body"], flags=re.M))
        full.append("\n\n")
    full_text = "".join(full)
    (DIST / "wmt-full.txt").write_text(full_text, encoding="utf-8")

    total_words = sum(s["words"] for s in sections)

    # manifest.json
    manifest = {
        "work": "The Way of Mercy and Truth",
        "subtitle": "A Curriculum of Formation in Three Pillars and Seven Stages",
        "author": "A. Pilgrim",
        "version": version,
        "license": "CC0 1.0 Universal (public domain dedication)",
        "total_words": total_words,
        "section_count": len(sections),
        "full_text": "dist/wmt-full.txt",
        "sections": [
            {"id": s["id"], "title": s["title"], "kind": s["kind"],
             "words": s["words"], "markdown": s["path"], "plain_text": s["txt"]}
            for s in sections
        ],
        "genealogy": [
            {"id": g["id"], "title": g["title"], "words": g["words"],
             "markdown": g["path"], "plain_text": g["txt"],
             "status": g.get("status", "stable")}
            for g in genealogy
        ],
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # llms.txt
    L = []
    L.append("# The Way of Mercy and Truth")
    L.append("")
    L.append("> A curriculum of Christian formation in three pillars (Truth, Humility, Mercy)")
    L.append("> and seven stages, drawn from the Christian East: Aphrahat, the Book of Steps,")
    L.append("> the Macarian Homilies, Isaac of Nineveh, Cassian, Ephrem, and the Didache.")
    L.append("")
    L.append(f"Version: {version}")
    L.append(f"Total: {total_words:,} words across {len(sections)} sections")
    L.append("License: CC0 1.0 — public domain. Free to quote, excerpt, translate, adapt, train on,")
    L.append("and redistribute, commercially or otherwise, with no attribution required.")
    L.append("")
    L.append("This work asks to be checked rather than trusted. Every claim it makes about")
    L.append("Scripture is mapped in the Scriptural Appendix; every place it departs from a")
    L.append("source is disclosed in A Note on the Witnesses.")
    L.append("")
    L.append("## Citation")
    L.append("")
    L.append("Cite by stable ID, not page number. IDs never change: WMT C23 is Chapter")
    L.append("Twenty-Three permanently, regardless of revisions to wording or file paths.")
    L.append("")
    L.append("## Where to start")
    L.append("")
    L.append("- New reader: WMT P0 (Preface), then WMT C01, then take up two practices for a year.")
    L.append("- Wanting the method first: WMT A1 (Praxis Appendix) — all 30 practices with difficulty ratings.")
    L.append("- Checking the sources: WMT A3 (Scriptural Appendix) and A Note on the Witnesses.")
    L.append("- Teaching a group: WMT A1 plus the reflection questions in each chapter.")
    L.append("")
    L.append("## Full text")
    L.append("")
    L.append("- [Complete curriculum, plain text](dist/wmt-full.txt)")
    L.append("")
    for kind, label in [("front-matter","## Front matter"),("stage","## Stages"),
                        ("chapter","## Chapters"),("appendix","## Appendices")]:
        group = [s for s in sections if s["kind"] == kind]
        if not group: continue
        L.append(label); L.append("")
        for s in group:
            L.append(f"- `{s['id']}` [{s['title']}]({s['txt']}) — {s['words']:,} words")
        L.append("")
    if genealogy:
        L.append("## Genealogy — where this came from")
        L.append("")
        L.append("Development record, not curriculum. Not needed to practice the Way.")
        L.append("")
        for g in genealogy:
            status = g.get("status", "stable")
            note = g.get("status_note", "")
            if status != "stable":
                mark = f"  *({status}{': ' + note if note else ''})*"
            else:
                mark = ""
            L.append(f"- `{g['id']}` [{g['title']}]({g['txt']}) — {g['words']:,} words{mark}")
        L.append("")

    (ROOT / "llms.txt").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"Built {len(sections)} sections + {len(genealogy)} genealogy files, {total_words:,} curriculum words, version {version}")
    print("  llms.txt")
    print("  manifest.json")
    print(f"  dist/wmt-full.txt ({len(full_text.split()):,} words)")
    print(f"  dist/*.txt ({len(sections)} files)")

if __name__ == "__main__":
    main()
