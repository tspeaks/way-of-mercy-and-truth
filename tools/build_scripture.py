#!/usr/bin/env python3
"""
build_scripture.py — render the scripture index into browsable pages.

    python3 tools/build_scripture.py

Reads every book file in index/*.json together with its text in index/text/*.json,
and writes:

    scripture.html              the index hub
    scripture-<book>.html       one page per indexed book

Each book page presents the passage in full, followed by what it anchors in the
curriculum. The text is the World English Bible, which is in the public domain.

Run after build.py and build_site.py so the shared styling stays in step.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index"
TEXT = INDEX / "text"

import importlib.util
_spec = importlib.util.spec_from_file_location("bs", ROOT / "tools" / "build_site.py")
_bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bs)
CSS, head, esc, CREST_SVG = _bs.CSS, _bs.head, _bs.esc, _bs.CREST_SVG

PILLAR_CLASS = {"truth": "t", "mercy": "m", "humility": "h"}

STAGE_NAMES = {
    "S1": "Foundations", "S2": "Perception", "S3": "Abiding", "S4": "Community",
    "S5": "Healing", "S6": "Transformation", "S7": "Mature Mercy",
}

EXTRA_CSS = """
.entry{border-top:1px solid var(--rule);padding:34px 0;}
.entry:first-of-type{border-top:0;}
.entry-ref{font-family:'IBM Plex Mono',monospace;font-size:11.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--gold-dim);margin:0 0 6px;}
.entry-name{font-family:'Cormorant Garamond',Georgia,serif;font-size:25px;font-weight:600;
  color:var(--gold-pale);margin:0 0 18px;letter-spacing:.02em;}
.passage{border-left:2px solid var(--gold-dim);padding:4px 0 4px 20px;margin:0 0 20px;
  background:rgba(201,162,39,.04);}
.passage p{margin:0 0 .7em;font-size:17px;line-height:1.65;color:var(--gold-pale);font-style:italic;}
.passage p:last-child{margin-bottom:0;}
.passage .vn{font-family:'IBM Plex Mono',monospace;font-style:normal;font-size:10.5px;
  color:var(--text-muted);vertical-align:3px;margin-right:5px;}
.conn{font-size:16.5px;line-height:1.6;color:var(--text);margin:0 0 16px;}
.tags{display:flex;flex-wrap:wrap;gap:7px;align-items:center;}
.tag{font-size:11px;letter-spacing:.06em;padding:4px 10px;border:1px solid var(--rule);
  color:var(--text-soft);text-decoration:none;white-space:nowrap;}
a.tag:hover{border-color:var(--gold-dim);color:var(--gold-bright);}
.tag.pillar{text-transform:uppercase;letter-spacing:.12em;}
.tag.pillar.t{border-color:var(--truth);color:var(--truth);}
.tag.pillar.m{border-color:var(--mercy);color:var(--mercy);}
.tag.pillar.h{border-color:var(--gold);color:var(--gold);}
.tag.conf{margin-left:auto;color:var(--text-muted);border-style:dashed;}
.tag.corrected{border-color:var(--gold);color:var(--gold);}
.tag.reviewed{border-color:var(--truth);color:var(--truth);}
.passage.cluster p{font-style:normal;color:var(--text);}
.passage.cluster .cref{color:var(--gold-dim);font-size:10.5px;margin-right:9px;vertical-align:2px;}
.cluster-note{font-size:12px;color:var(--text-muted);letter-spacing:.06em;margin:0 0 12px;font-style:italic;}
.entry-ref.cluster-label{color:var(--gold);}
.tag.kind{border-style:solid;border-color:var(--gold-dim);color:var(--gold);
  text-transform:uppercase;letter-spacing:.12em;font-size:10px;}
.tag.mode{text-transform:uppercase;letter-spacing:.12em;font-size:10px;border-style:dotted;}
.tag.mode.prescribes{border-color:var(--gold);color:var(--gold);}
.tag.mode.exemplifies{border-color:var(--truth);color:var(--truth);}
.tag.mode.counter{border-color:var(--mercy);color:var(--mercy);}
.booknav{display:flex;flex-wrap:wrap;gap:10px;margin:26px 0 0;}
.stat{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:24px 0 0;}
@media (min-width:560px){ .stat{grid-template-columns:repeat(4,1fr);} }
.stat div{border:1px solid var(--rule);background:var(--bg-raised);padding:14px;text-align:center;}
.stat b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:26px;
  color:var(--gold-pale);font-weight:600;}
.stat span{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-muted);}
"""


REF_RE = re.compile(r"^(.+?)\s+(\d+):(\d+)(?:[-–](?:(\d+):)?(\d+))?$")


def ref_verses(text_data, ref):
    """(chapter, verse) pairs for a reference, crossing chapter boundaries if needed."""
    m = REF_RE.match(ref)
    if not m:
        return []
    c1, v1 = int(m.group(2)), int(m.group(3))
    c2 = int(m.group(4)) if m.group(4) else c1
    v2 = int(m.group(5)) if m.group(5) else v1
    counts = {}
    for k in text_data["verses"]:
        c, v = (int(x) for x in k.split(":"))
        counts[c] = max(counts.get(c, 0), v)
    out = []
    for c in range(c1, c2 + 1):
        lo = v1 if c == c1 else 1
        hi = v2 if c == c2 else counts.get(c, 0)
        for v in range(lo, hi + 1):
            body = text_data["verses"].get(f"{c}:{v}")
            if body:
                out.append((f"{c}:{v}", body))
    return out



def render_cluster(text_data, refs):
    """A cluster gathers scattered verses on one theme; render each with its reference."""
    out = ['<div class="passage cluster">']
    for r in refs:
        for vref, body in ref_verses(text_data, r):
            out.append(f'<p><span class="cref mono">{vref}</span>{esc(body)}</p>')
    out.append("</div>")
    return "\n".join(out)


def render_passage(text_data, ref):
    out = ['<div class="passage">']
    for vref, body in ref_verses(text_data, ref):
        out.append(f'<p><span class="vn">{vref.split(":")[1]}</span>{esc(body)}</p>')
    out.append("</div>")
    return "\n".join(out)


def book_page(data, text_data):
    book = data["book"]
    entries = data["entries"]
    L = head(f'{book} — Scripture Index — The Way of Mercy and Truth',
             f'Every passage of {book} mapped to the stages, chapters, and practices '
             f'of The Way of Mercy and Truth. World English Bible, public domain.')
    a = L.append
    a(f"<style>{EXTRA_CSS}</style>")

    a('<div class="topbar"><div class="wrap">')
    a('<a class="home" href="index.html">✦ The Way of Mercy and Truth</a>')
    a(f'<span class="where mono">{esc(book)} · index</span>')
    a('</div><div class="progress"><i></i></div></div>')

    a('<main id="main"><article>')
    a('<div class="doc-head">')
    a('<p class="doc-kicker">Scripture Index</p>')
    a(f'<h1 class="doc-title">{esc(book)}</h1>')
    a('<p class="doc-sub">World English Bible · public domain</p>')
    covered = set()
    for e in entries:
        for r in (e["refs"] if e.get("kind") == "cluster" else [e["ref"]]):
            covered |= {v for v, _ in ref_verses(text_data, r)}
    a(f'<p class="doc-meta mono">{len(entries)} passages · '
      f'{len(covered)} of {len(text_data["verses"])} verses</p>')
    a("</div>")

    a('<div class="doc-body">')
    for e in entries:
        a('<div class="entry">')
        a(f'<p class="entry-ref">{esc(e["ref"])}</p>')
        a(f'<h2 class="entry-name">{esc(e["pericope"])}</h2>')
        if e.get("kind") == "cluster":
            a(f'<p class="cluster-note">{len(e["refs"])} passages gathered from across '
              f'the collection</p>')
            a(render_cluster(text_data, e["refs"]))
        else:
            a(render_passage(text_data, e["ref"]))
        if e.get("synoptic_parallel"):
            a(f'<p class="cluster-note">Also in Luke: {esc(e["synoptic_parallel"])}</p>')
        a(f'<p class="conn">{esc(e["connection"])}</p>')
        a('<div class="tags">')
        if e.get("kind") == "cluster":
            a('<span class="tag kind">thematic cluster</span>')
        if e.get("mode"):
            cls = {"prescribes":"prescribes","exemplifies":"exemplifies",
                   "counter-example":"counter"}[e["mode"]]
            label = {"prescribes":"commands it","exemplifies":"shows it done",
                     "counter-example":"shows its absence"}[e["mode"]]
            a(f'<span class="tag mode {cls}">{esc(label)}</span>')
        for p in e["pillars"]:
            a(f'<span class="tag pillar {PILLAR_CLASS[p]}">{esc(p)}</span>')
        for s in e["stages"]:
            a(f'<span class="tag">{esc(s)} {esc(STAGE_NAMES.get(s, ""))}</span>')
        for c in e["chapters"]:
            n = int(c[1:])
            a(f'<a class="tag" href="c{n:02d}.html">{esc(c)}</a>')
        for pr in e["practices"]:
            a(f'<a class="tag" href="a1.html">{esc(pr)}</a>')
        if e.get("author_corrected"):
            a('<span class="tag corrected">author placed</span>')
        if e.get("review"):
            a('<span class="tag reviewed">amended at review</span>')
        a(f'<span class="tag conf mono">{esc(e["confidence"])}</span>')
        a("</div>")
        a("</div>")
    a("</div>")
    a("</article>")

    a('<nav class="docnav">')
    a('<p class="rule-orn orn"><span>✦</span></p>')
    a('<p class="nav-hub"><a href="scripture.html">All indexed books</a> · '
      '<a href="index.html">Table of contents</a></p>')
    a("</nav>")
    a("</main></body></html>")
    return "\n".join(L) + "\n"


def hub_page(books):
    L = head("Scripture Index — The Way of Mercy and Truth",
             "Scripture mapped passage by passage to the stages, chapters, and practices "
             "of The Way of Mercy and Truth. Public domain.")
    a = L.append
    a(f"<style>{EXTRA_CSS}</style>")

    a('<div class="topbar"><div class="wrap">')
    a('<a class="home" href="index.html">✦ The Way of Mercy and Truth</a>')
    a('<span class="where mono">Scripture index</span>')
    a("</div></div>")

    a('<main id="main"><div class="wrap">')
    a('<header class="masthead">')
    a(CREST_SVG)
    a('<p class="kicker mono">In progress</p>')
    a('<h1 class="title display">The Scripture Index</h1>')
    a('<p class="subtitle">Every passage, and what it anchors — set beside the text itself, '
      'so that you can check the claim without leaving the page.</p>')
    a("</header>")

    a("<section>")
    a('<h2 class="sec display">What this is</h2>')
    a('<p class="section-note">The Scriptural Appendix tells you which books this road draws '
      'on. This goes the other way: it works through Scripture passage by passage and records '
      'what each one anchors — which stage, which chapter, which practice, and which of the '
      'three pillars it serves. Where a passage anchors nothing, it is left alone rather than '
      'stretched to fit.</p>')
    a('<p class="section-note">The text is the World English Bible, which is in the public '
      'domain, so the passage can sit here in full rather than as a reference you have to go '
      'and look up. The whole index is CC0, like everything else here.</p>')

    total_e = sum(len(b["data"]["entries"]) for b in books)
    total_v = sum(len(b["text"]["verses"]) for b in books)
    a('<div class="stat">')
    a(f'<div><b>{len(books)}</b><span>books indexed</span></div>')
    a(f'<div><b>{total_e}</b><span>passages</span></div>')
    a(f'<div><b>{total_v}</b><span>verses</span></div>')
    a('<div><b>66</b><span>books in all</span></div>')
    a("</div>")
    a("</section>")

    a("<section>")
    a('<h2 class="sec display">Indexed so far</h2>')
    a('<ul class="linklist">')
    for b in books:
        d = b["data"]
        a(f'<li><a href="scripture-{d["book"].lower().replace(" ", "-")}.html">'
          f'<span class="lt">{esc(d["book"])}</span>'
          f'<span class="ld">{len(d["entries"])} passages · '
          f'{esc(d.get("status", "complete"))}</span>'
          "</a></li>")
    a("</ul>")
    a('<p class="section-note" style="margin-top:22px;">The rest of the canon is not yet done. '
      'This is a work in progress and is published as one, because a partial index that is '
      'honest about being partial is more use than a finished one that is quietly wrong.</p>')
    a("</section>")

    a("<section>")
    a('<h2 class="sec display">How to read an entry</h2>')
    a('<div class="warn">')
    a("<h3>The tags are claims, and claims can be wrong.</h3>")
    a("<p>Each entry carries a confidence marking. A passage marked <em>medium</em> is one "
      "where the connection seemed real but not certain — treat it as a question rather than "
      "a finding. Entries marked <em>author placed</em> were assigned by the author directly.</p>")
    a("<p>If a connection here does not survive your own reading of the passage, the passage "
      "wins. That is the same instruction the Scriptural Appendix gives, and it is meant just "
      "as plainly here.</p>")
    a("</div>")
    a("</section>")
    a("</div></main>")

    a('<footer><div class="wrap">')
    a('<p class="mono">Scripture quotations from the World English Bible · public domain</p>')
    a('<p><a href="index.html">Table of contents</a> · <a href="a3.html">Scriptural Appendix</a></p>')
    a("<p>Dedicated to the public domain. Go and do likewise.</p>")
    a("</div></footer></body></html>")
    return "\n".join(L) + "\n"


def build():
    books = []
    for f in sorted(INDEX.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        tf = TEXT / f.name
        if not tf.exists():
            print(f"  ! {f.name}: no text file at index/text/{f.name} — skipped")
            continue
        text = json.loads(tf.read_text(encoding="utf-8"))
        books.append({"data": data, "text": text})
        slug = data["book"].lower().replace(" ", "-")
        (ROOT / f"scripture-{slug}.html").write_text(
            book_page(data, text), encoding="utf-8")
        print(f"  scripture-{slug}.html — {len(data['entries'])} passages, "
              f"{len(text['verses'])} verses")

    books.sort(key=lambda b: b["text"].get("canonical_order") or 999)
    (ROOT / "scripture.html").write_text(hub_page(books), encoding="utf-8")
    print(f"Built scripture.html + {len(books)} book page(s)")


if __name__ == "__main__":
    build()
