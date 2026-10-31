#!/usr/bin/env python3
"""Check that quotations inside index connections match the WEB text.

Usage:  python3 tools/check_quotes.py [book-slug ...]     (no args = every book)

For each entry, every passage set in single quotation marks inside the
`connection` field is split on ellipses and semicolons, normalised (quote
marks, dashes and whitespace), and looked for in the book's own WEB text,
then in the whole WEB corpus (for cross-references), then in the trunk
markdown (for quotations of the curriculum and appendices). Fragments
shorter than 14 characters and fragments containing editorial brackets
are skipped. Anything not found is printed as  book | ref | fragment.

Pericope titles are labels and are not checked. The parser treats an
apostrophe between two letters or digits as part of a word, so a few
possessives can still produce false positives; read each flag before
changing anything.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"')):
        s = s.replace(a, b)
    s = s.replace("'", "").replace('"', "")
    s = re.sub(r"[-–—]", " ", s)
    return re.sub(r"\s+", " ", s).lower()


def main(argv):
    texts = {}
    for f in glob.glob(os.path.join(ROOT, "index", "text", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        texts[os.path.basename(f)[:-5]] = norm(" ".join(d["verses"].values()))
    corpus = " ".join(texts.values())
    trunk = " ".join(norm(open(f, encoding="utf-8").read())
                     for f in glob.glob(os.path.join(ROOT, "trunk", "**", "*.md"), recursive=True))
    books = argv or sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, "index", "*.json")))
    checked = unmatched = 0
    for b in books:
        path = os.path.join(ROOT, "index", f"{b}.json")
        if not os.path.exists(path):
            continue
        own = texts.get(b, "")
        for e in json.load(open(path, encoding="utf-8"))["entries"]:
            for q in re.findall(r"(?<![A-Za-z0-9])'(.+?)'(?![A-Za-z0-9])", e["connection"]):
                for frag in re.split(r"…|\.\.\.|;", q):
                    if "[" in frag:
                        continue
                    f = norm(frag).strip(" .,;:!?()")
                    if len(f) < 14:
                        continue
                    checked += 1
                    if f in own or f in corpus or f in trunk:
                        continue
                    unmatched += 1
                    print(f"{b} | {e['ref']} | {f[:160]}")
    print(f"checked {checked} fragments; unmatched {unmatched}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
