# The Way of Mercy and Truth Code Walkthrough

A guided tour of every piece of this repository's code: what each block does,
how it works, and how it connects to the rest. Read top to bottom the first
time; after that, jump to the part you're curious about.

## At a glance

| | |
|---|---|
| **What it is** | The source and the publishing machinery for a 29-chapter curriculum of Christian formation: markdown manuscript in, a static website, plain-text editions, a machine-readable index and a scripture index out |
| **Built with** | Markdown with small frontmatter blocks (the text), Python 3 standard library only (the tools), static HTML and CSS (the site), GitHub Pages (hosting) |
| **Run it** | `python3 tools/build.py`, then `python3 tools/build_site.py`, then `python3 tools/build_scripture.py`. The output is committed; Pages serves the repo root |
| **Test it** | `python3 tools/check_index.py index/<book>.json` validates a scripture index file and exits non-zero on structural errors. `python3 wmt_index_coverage.py` reports coverage |
| **Where it stands** | Version 1.0.1, live at wayofmercyandtruth.org. The scripture index covers fourteen books, all reviewed |

---

## Introduction: the forest before the trees

This repo is a small publishing house. The writing lives in one place, and three
scripts turn it into everything a reader, a search engine or a language model
might want:

```
   The text (you edit)                Build tools (Python)                 The output (committed)
┌───────────────────────┐        ┌──────────────────────────┐        ┌──────────────────────────┐
│ trunk/                │        │ 1 tools/build.py         │ ─────▶ │ manifest.json            │
│  preface, stages s1-7,│ ─────▶ │   parse frontmatter,     │        │ llms.txt                 │
│  chapters c01-c29,    │        │   order by ID, count     │        │ dist/*.txt, wmt-full.txt │
│  appendices           │        └────────────┬─────────────┘        ├──────────────────────────┤
│ genealogy/            │                     │ manifest.json        │ index.html, c01…c29.html │
│  development record   │                     ▼                      │ s1…s7, a1…a3, g00…g10,   │
└───────────────────────┘        ┌──────────────────────────┐ ─────▶ │ preface.html, 404.html   │
┌───────────────────────┐        │ 2 tools/build_site.py    │        ├──────────────────────────┤
│ index/<book>.json     │        └──────────────────────────┘        │ scripture.html,          │
│  passage → stage,     │        ┌──────────────────────────┐ ─────▶ │ scripture-<book>.html    │
│  chapter, practice    │ ─────▶ │ 3 tools/build_scripture  │        └──────────────────────────┘
│ index/text/ (WEB)     │        └──────────────────────────┘
└───────────────────────┘        check_index.py · wmt_index_coverage.py · build_review_package.py
```

1. **The trunk** (`trunk/`) is the curriculum itself: a preface, seven stage
   introductions, twenty-nine chapters and three appendices, one markdown file
   each. Every file starts with a small frontmatter block giving its permanent
   ID (`WMT C01`), title and kind.
2. **The build** (`tools/build.py`) reads the trunk and writes the
   machine-readable layer: a JSON manifest, an `llms.txt` index, and plain-text
   editions of every section and of the whole work.
3. **The site** (`tools/build_site.py`) reads the manifest and the markdown and
   writes one self-contained HTML page per section, with reading-order
   navigation.
4. **The scripture index** (`index/`, `tools/build_scripture.py` and its
   helpers) maps passages of Scripture to the stages, chapters and practices they
   anchor, and renders them next to the full passage text.

Why generate everything from the trunk? So the site, the plain text and the
index can never disagree with the book. Fix a sentence in one markdown file,
rebuild, and every edition carries the fix.

One idea runs through the whole repo: **check me rather than trust me.** IDs are
permanent so a citation never breaks. Every edition is plain and public-domain so
anyone can verify it. The scripture index records a confidence and a connection
for every tag, the checker refuses malformed entries, and reviewers get the
passage and the claim side by side. The code is built to make the work easy to
audit.

The tour goes in build order: the trunk's format, `build.py`, `build_site.py`,
the scripture index and its tools, then the release workflow.

### Words you'll meet

- **Trunk**: the canonical text of the curriculum, in `trunk/`.
- **Stable ID**: `WMT P0` (preface), `WMT S1`–`S7` (stages), `WMT C01`–`C29`
  (chapters), `WMT A1`–`A3` (appendices), `WMT G00`… (genealogy), and `PR01`–`PR30`
  (practices). IDs never change and are never reused.
- **Frontmatter**: the block between `---` lines at the top of a markdown file
  holding fields like `id`, `title`, `kind`.
- **Static site**: plain HTML files with no server code and no build step on
  the host; GitHub Pages just serves them.
- **`llms.txt`**: a plain index at the site root meant for language models and
  people, listing every section with a link to its plain text.
- **WEB**: the World English Bible, a public-domain translation, used for every
  quoted passage.
- **Pericope**: a passage read as one unit.

---

## Part 1: The trunk's format

```markdown
---
id: "WMT C01"
title: "Chapter One: The Ground Beneath Everything"
kind: chapter
words: 2142
---

# Chapter One: The Ground Beneath Everything

Stage One — Foundations: How should one live?
```

Every section is a markdown file with frontmatter and a body. The body uses a
deliberately narrow slice of markdown: headings, paragraphs, and scripture
citation lines. That narrowness is a design choice: the site generator only has
to understand what the book actually uses, so it can be a small, readable
function instead of a full markdown library.

`kind` is one of `front-matter`, `stage`, `chapter`, `appendix`. `genealogy/`
uses the same format for the development record (where the curriculum came
from), which is published but marked as not needed to practice the Way.

---

## Part 2: The machine-readable layer (`tools/build.py`)

### 2.1 Reading a section

```python
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
```

`parse` splits a file into its frontmatter and body with one regular expression,
then reads each `key: value` line. It's a hand-rolled frontmatter reader rather
than a YAML library, which keeps the tools standard-library only: nothing to
install, nothing to break.

### 2.2 Putting sections in reading order

```python
def sort_key(s):
    sid = s["id"]
    num = re.search(r"(\d+)", sid)
    n = int(num.group(1)) if num else 0
    if sid.startswith("WMT P"): return (0, 0)
    if sid.startswith("WMT G"): return (4, n)
    if sid.startswith("WMT S"): return (1, n)
    if sid.startswith("WMT C"): return (2, n)
    return (3, n)
```

Files are found with `rglob("*.md")` in whatever order the disk gives, so
`sort_key` imposes the book's order from the IDs: preface first, then stages,
chapters, appendices, and genealogy last. Sorting by a tuple `(group, number)`
sorts by group first and number second, so "C2" comes before "C10" (a plain text
sort would put "C10" first).

### 2.3 What it writes

For each section it strips the markdown markers (`#` headings, `*italics*`) to
make a plain-text edition in `dist/`, counts the words, and records the paths.
Then it writes:

- **`dist/wmt-full.txt`**: the whole curriculum as one file, each section headed
  `=== WMT C01 — Chapter One… ===`.
- **`manifest.json`**: the structured index (work, version, license, total
  words, and for every section its ID, title, kind, word count and both paths).
  The site builder reads this.
- **`llms.txt`**: a readable index with the citation rule ("cite by stable ID,
  not page number"), where to start for each kind of reader, and a link to every
  plain-text section with its word count.

The version comes from the `VERSION` file, so a release is one number change and
a rebuild.

---

## Part 3: The website (`tools/build_site.py`)

### 3.1 Configuration at the top

```python
GITHUB_USER = "tspeaks"
GITHUB_REPO = "way-of-mercy-and-truth"
GITHUB_BRANCH = "main"
CUSTOM_DOMAIN = "wayofmercyandtruth.org"   # set to "" to disable the CNAME file

STAGE_CHAPTERS = {
    "WMT S1": (1, 5),
    "WMT S2": (6, 8),
    ...
```

Everything that would change if the site moved lives in a few constants at the
top. `STAGE_CHAPTERS` maps each stage to its chapter range; the comment explains
that the ranges come from what each stage's own text says ("five chapters of
footings…") and that they sum to exactly 29, which is the check.

### 3.2 A small markdown renderer

```python
def render_markdown(md_text):
    ...
    for raw in body.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("### "):
            out.append(f"<h3>{esc(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{esc(line[3:])}</h2>")
        elif line.startswith("# "):
            if not first_h1_dropped:
                first_h1_dropped = True
                continue
        else:
            m = SCRIPTURE_RE.match(line)
            if m:
                out.append('<blockquote class="scripture">' ...
```

Line by line: headings become `<h2>`/`<h3>`, the first `#` title is dropped
(the page template prints it), scripture citation lines become styled
blockquotes, and everything else becomes a paragraph. Every piece of text passes
through `esc()`, which escapes `<`, `>` and `&`, so the text can never be
mistaken for HTML.

### 3.3 Building the pages

```python
for i, s in enumerate(order):
    prev_s = order[i - 1] if i > 0 else None
    next_s = order[i + 1] if i < len(order) - 1 else None
    ...
    if s["kind"] == "chapter":
        kicker = f'{sid.replace("WMT ", "")} · Stage {st_id[-1]}'
        subtitle = f'{stage_name} — {STAGE_QUESTIONS.get(st_id, "")}'
        pos = f"Chapter {chapter_index[sid]} of {len(chapters)}"
```

`build_reading_order` lays the sections out in the order a reader meets them
(a stage introduction, then its chapters). Each page gets its previous and next
neighbor for navigation, a small "kicker" line (`C07 · Stage 2`), a subtitle with
the stage's question ("How should one see?"), and its position ("Chapter 7 of
29"). `doc_page` assembles the full HTML: `head()` adds the title and
description, then the rendered body and the previous/next navigation, with
shared footer links to the repository's governance documents.

Every page is self-contained: no JavaScript is required to read anything, and
arrow-key navigation is a progressive enhancement on top. The script also writes
the hub (`index.html`), the genealogy pages, a `404.html`, the `CNAME` file for
the custom domain, and `.nojekyll` so GitHub Pages serves the files as-is.

---

## Part 4: The scripture index (`index/`)

### 4.1 One entry

```json
{
  "ref": "Ruth 1:1-5",
  "pericope": "A famine, a sojourn, and three graves in Moab",
  "pillars": ["truth"],
  "stages": ["S5"],
  "chapters": ["C19"],
  "practices": [],
  "mode": "exemplifies",
  "connection": "Five verses cover a decade: a famine, a move abroad, two marriages, and three deaths. ...",
  "confidence": "high",
  "prior": false
}
```

Each indexed book is one JSON file of entries. An entry says which passage, what
it's about, which pillars, stages, chapters and practices it anchors, and *why*
(`connection`). `confidence` (high, medium, low) is the indexer's honesty about
how strong the link is. `mode` (for narrative books) says whether a passage
commands a practice, shows it done, or shows what its absence costs. The file
also records the `method_version` used and a note about the book.

The Bible text itself lives separately in `index/text/<book>.json`, one file per
book, made once by `tools/ingest_web.py` from the public-domain WEB plain text.
After that, indexing a new book needs no network.

### 4.2 The checker: `tools/check_index.py`

```python
STAGES = {f"S{i}" for i in range(1, 8)}
CHAPTERS = {f"C{i:02d}" for i in range(1, 30)}
PRACTICES = {f"PR{i:02d}" for i in range(1, 31)}
...
for f in REQUIRED:
    if f not in e:
        errors.append(f"{where}: missing field '{f}'")
```

Hand-indexing makes errors that are invisible by eye, so the checker catches
them. **Errors** (it exits non-zero, so it can gate a commit): missing fields, a
tag that points at a stage, chapter or practice that doesn't exist, an invalid
mode or confidence, a reference it can't parse, and verse ranges that overlap.
`expand` turns "Jeremiah 1:4-2:3" into every verse it covers, using the real
verse counts from the text file, which is how overlaps and gaps are found.
**Warnings**: no pillar or stage, a connection under twelve words, and one
specific mistake the project has made three times: a counter-example whose prose
names a practice but whose `practices` list is empty.

It also reports coverage (which practices and chapters this book anchors and
which it doesn't) with a reminder that absence is information, not failure: a
book that anchors everything is more likely badly indexed than unusually rich.

### 4.3 Rendering and reviewing

`tools/build_scripture.py` renders `scripture.html` (the hub) and one
`scripture-<book>.html` per indexed book. Each passage is printed in full from
the WEB text, followed by what it anchors in the curriculum. It loads
`build_site.py` as a module so the pages share the site's styling.

`tools/build_review_package.py` writes `index/reviews/<book>-package.md`: every
passage and its claim side by side. The docstring explains the reason with
evidence: reviewers handed only references raised flags about practice
definitions but never caught a misreading, because they were judging from
memory. The package lets a reviewer check whether a connection survives contact
with the actual verses. The `index/reviews/*-pass2.json` files and
`SYNTHESIS-PASS.json` are the results of those reviews.

`wmt_index_coverage.py` reads every indexed book, prints how many passages land
on each chapter and practice (heaviest first) and which books feed each, and
writes `by-chapter.json`, the same entries regrouped by chapter and practice
instead of by book. That regrouped file is what a devotional generator would
read. `--debug` prints samples of what it parsed when the counts look wrong.

---

## Part 5: Checks, tools and releases

There's no test suite in the usual sense; the checks are tools you run on the
data:

| Tool | What it proves |
|---|---|
| `tools/check_index.py index/<book>.json` | Every entry has its fields, every tag points at a real stage, chapter, practice or pillar, references parse, verse ranges don't overlap. Exits non-zero on errors |
| `wmt_index_coverage.py` | Which chapters and practices the index anchors and which books feed them; writes `by-chapter.json` |
| `tools/build_review_package.py` | Each claim can be checked against the full passage it cites |
| `tools/build.py` | The trunk parses: every section has frontmatter, and word counts and paths land in the manifest |


```bash
python3 tools/build.py     # regenerates llms.txt, manifest.json, dist/
git add -A
git commit -m "C23: <what changed and why>"
```

`SETUP.md` and `VERSIONING.md` hold the workflow. After any edit, rebuild and
commit with a message naming the section ID. Versions follow `MAJOR.MINOR.PATCH`
with meanings specific to a teaching text: PATCH changes no meaning (typos,
links), MINOR improves expression with the teaching unchanged, MAJOR changes the
teaching itself and requires a changelog entry saying what a reader who learned
the old version should now understand differently. Three rules are absolute:
IDs never change, every MAJOR has a changelog entry, and published history is
never rewritten ("an untraceable road cannot be checked by anyone").

`.github/ISSUE_TEMPLATE/` provides two forms, `correction.md` and
`field-report.md`: the "check me" apparatus in working form. `practices.json`
lists the thirty practices with their permanent IDs and the note "take up two
and hold them for a year before adding a third."

---

## Conclusion: how the pieces make one product

Step back and the trees form a forest with three ideas running through it.

**First, one source, many editions.** The trunk is the only place the text
lives. The manifest, the plain text, `llms.txt`, the website and the scripture
pages are all generated from it, so they can't drift apart.

**Second, permanence makes it citable.** Stable IDs that never change or get
reused, a versioning scheme that separates wording from teaching, and history
that's never rewritten. Someone who cites `WMT C23` today will find the same
chapter in ten years.

**Third, built to be checked.** Every scripture tag carries its reason and its
confidence, the checker rejects malformed entries and flags thin ones, reviewers
see the passage beside the claim, and everything is public domain and plain
text. The code serves the book's own posture: check the teacher rather than
trust him.

If you follow one thread end to end, follow a fix to Chapter Seven. You edit
`trunk/chapters/c07-cleansing-the-eyes.md`; `build.py` parses its frontmatter,
sorts it after C06, writes `dist/c07-cleansing-the-eyes.txt`, updates its word
count in `manifest.json` and `llms.txt`, and rewrites `wmt-full.txt`;
`build_site.py` reads the manifest, renders the markdown through
`render_markdown`, and writes `c07.html` with C06 and C08 as neighbors; you commit
with "C07: …" and Pages serves it. That path touches every build tool.

### Saying it out loud

- **One sentence:** It's the source for a Christian formation curriculum plus a
  small set of Python scripts that publish it as a website, plain-text editions
  and a scripture index from one set of markdown files.
- **Thirty seconds:** The book lives as markdown files, one per chapter, each
  with a permanent ID. A build script turns them into a JSON manifest, a
  plain-text edition of every chapter, and an index for language models. A
  second script turns the manifest into a static website with reading-order
  navigation, and a third renders a scripture index that maps Bible passages to
  the chapters and practices they support, each with a written reason and a
  confidence level. A checker validates the index before anything is committed.
  Everything is standard-library Python and plain HTML, so nothing needs
  installing and nothing can quietly break.
- **"Why not use a static site generator?"** The book uses a tiny slice of
  markdown, so a hundred lines of Python does the job with nothing to install,
  and every line of it can be read and checked.
- **"Why the permanent IDs?"** So citations never break, whatever changes in
  wording or file paths.
- **"How do you keep the scripture index honest?"** Every tag has a written
  connection and a confidence, a checker rejects malformed or invalid entries,
  and reviewers see the passage text beside each claim.

### Where it connects to the author's other projects

This repository stands on its own. One private companion app reads the
curriculum's structure (practice IDs like PR07 and PR11, chapter and stage
titles) extracted from the manuscript, which is one more reason the IDs are
permanent: other tools depend on them. The book is a calling, not a product, and
it's kept separate from the author's business repositories on purpose.

### Good places to start asking questions

Why the tools avoid outside libraries; how `sort_key` keeps C2 before C10; how
`check_index.py` finds overlapping verse ranges across chapter boundaries; or
what a devotional generator reading `by-chapter.json` would look like.

---

*One of ten walkthroughs written as a set, all at `docs/code-walkthrough.md`;
the other nine cover the author's private projects.*
