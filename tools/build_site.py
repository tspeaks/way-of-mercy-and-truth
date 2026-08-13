#!/usr/bin/env python3
"""
build_site.py — generates index.html, a static hub for The Way of Mercy and Truth.

Reads manifest.json (produced by build.py) so the page never drifts from the
curriculum. Run build.py first, then this.

    python3 tools/build.py
    python3 tools/build_site.py

Output: index.html at the repo root. No dependencies, no build step, no
JavaScript required to read the page.

EDIT THIS if you rename the repo or use a different GitHub account:
"""

import json
from pathlib import Path

GITHUB_USER = "tspeaks"
GITHUB_REPO = "way-of-mercy-and-truth"
GITHUB_BRANCH = "main"

ROOT = Path(__file__).resolve().parent.parent
BLOB = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/"

# Stage -> chapter ranges.
# Derived from the chapter counts each stage file states in its own text
# ("five chapters of footings", "Six chapters.", "Four chapters.",
# "Three chapters remain."). They sum to exactly 29, which is the check.
STAGE_CHAPTERS = {
    "WMT S1": (1, 5),
    "WMT S2": (6, 8),
    "WMT S3": (9, 12),
    "WMT S4": (13, 18),
    "WMT S5": (19, 22),
    "WMT S6": (23, 26),
    "WMT S7": (27, 29),
}

STAGE_QUESTIONS = {
    "WMT S1": "How should one live?",
    "WMT S2": "How should one see?",
    "WMT S3": "How does one remain?",
    "WMT S4": "How should people live together?",
    "WMT S5": "How is the heart healed?",
    "WMT S6": "How does the heart change?",
    "WMT S7": "What does the transformed person become?",
}

STATUS_BLURB = {
    "stable": "Development record, standing as recorded.",
    "partial": "Some claims superseded; others still load-bearing.",
    "speculative": "Narrative and theological experiment. Nothing depends on it.",
}


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


CSS = """
:root{
  --bg:#0F0E0A; --bg-raised:#1A1915;
  --gold:#D4AF37; --gold-dark:#A68A3B; --gold-light:#E8D5B7;
  --text:#E8D5B7; --text-soft:#C9B89A; --text-muted:#8B7E6B;
  --accent-truth:#6FA8B8; --accent-mercy:#C97862; --accent-spec:#9B88B0;
  --line:rgba(212,175,55,0.22); --line-strong:rgba(212,175,55,0.4);
  --focus:#D4AF37;
  --shadow:0 2px 8px rgba(0,0,0,.6), 0 8px 24px rgba(212,175,55,.08);
}
@media (prefers-color-scheme: dark){
  :root{
    --parchment:#191E1B; --paper:#1F2622; --raised:#28312B;
    --ink:#E9E3D5; --ink-soft:#C3BDAF; --muted:#948B79;
    --truth:#8FB6C1; --mercy:#D89578; --gold:#D4AC53; --gold-line:#C9A227;
    --spec:#B4A2C4;
    --line:rgba(233,227,213,0.14); --line-strong:rgba(233,227,213,0.3);
    --focus:#8FB6C1;
    --shadow:0 1px 2px rgba(0,0,0,.3), 0 4px 14px rgba(0,0,0,.22);
  }
}
*,*::before,*::after{box-sizing:border-box;}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;}
@media (prefers-reduced-motion: reduce){
  html{scroll-behavior:auto;}
  *,*::before,*::after{animation-duration:.01ms !important;transition-duration:.01ms !important;}
}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:'Source Serif 4','Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif;
  font-size:17px; line-height:1.6;
  -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
  background-attachment:fixed;
}
img{max-width:100%;height:auto;}
a{color:var(--gold);text-decoration-thickness:1px;text-underline-offset:2px;transition:color .2s ease;}
a:hover{color:var(--gold-light);}
:focus-visible{outline:2px solid var(--focus);outline-offset:3px;border-radius:2px;}
.wrap{max-width:820px;margin:0 auto;padding:0 20px;}
.skip{position:absolute;left:-9999px;top:0;background:var(--bg-raised);color:var(--gold);
  padding:10px 16px;z-index:99;border:1px solid var(--line-strong);border-radius:0 0 6px 0;}
.skip:focus{left:0;}
.mono{font-family:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;}
.display{font-family:'Fraunces','Iowan Old Style',Georgia,serif;font-weight:600;letter-spacing:-.012em;color:var(--gold);}

/* ---------- setup banner (disappears once configured) ---------- */
.setup{background:rgba(201,120,98,.15);border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);color:var(--gold-light);font-size:14px;padding:10px 0;}
.setup .wrap{display:flex;gap:10px;flex-wrap:wrap;align-items:baseline;}
.setup code{background:rgba(212,175,55,.2);padding:1px 6px;border-radius:3px;font-size:13px;color:var(--gold);}

/* ---------- masthead ---------- */
header.masthead{padding:56px 0 40px;border-bottom:2px solid var(--line-strong);position:relative;}
header.masthead::before,header.masthead::after{
  content:"✦"; position:absolute; left:20px; font-size:16px; color:var(--gold);
}
header.masthead::before{top:20px;}
header.masthead::after{bottom:20px;}
.kicker{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-muted);margin:0 0 14px;}
h1.title{font-size:clamp(32px,8vw,54px);line-height:1.03;margin:0 0 10px;color:var(--gold);}
.subtitle{font-size:clamp(16px,3.4vw,19px);color:var(--text-soft);font-style:italic;margin:0 0 26px;}
blockquote.epigraph{
  margin:0 0 26px; padding:0 0 0 18px; border-left:3px solid var(--gold);
  font-size:clamp(16px,3.5vw,19px); color:var(--text-soft); line-height:1.45;
}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:26px;}
.badge{font-size:11.5px;letter-spacing:.04em;padding:5px 10px;border-radius:999px;
  border:1px solid var(--line);color:var(--text-muted);background:rgba(212,175,55,.08);white-space:nowrap;}
.badge.gold{border-color:var(--line-strong);color:var(--gold);background:rgba(212,175,55,.15);}
.cta-row{display:flex;flex-wrap:wrap;gap:12px;}
.btn{
  display:inline-block;padding:13px 22px;border-radius:4px;text-decoration:none;
  font-size:15.5px;font-weight:600;border:1px solid var(--gold);
  background:transparent;color:var(--gold);box-shadow:var(--shadow);
  min-height:44px;transition:all .2s ease;
}
.btn:hover{background:rgba(212,175,55,.1);border-color:var(--gold-light);color:var(--gold-light);}
.btn.primary{background:var(--gold);border-color:var(--gold);color:var(--bg);}
.btn.primary:hover{background:var(--gold-light);border-color:var(--gold-light);box-shadow:0 0 20px rgba(212,175,55,.3);}

/* ---------- generic section ---------- */
section{padding:46px 0;border-bottom:1px solid var(--line);}
section:last-of-type{border-bottom:0;}
h2{font-size:clamp(22px,5vw,28px);margin:0 0 6px;color:var(--gold);}
.section-note{color:var(--text-soft);margin:0 0 24px;max-width:62ch;}
h3{font-size:17px;margin:0 0 4px;color:var(--text);}

/* ---------- start-here cards ---------- */
.cards{display:grid;gap:14px;grid-template-columns:1fr;}
@media (min-width:660px){ .cards{grid-template-columns:1fr 1fr;} }
.card{background:var(--bg-raised);border:1px solid var(--line);border-radius:6px;padding:18px 20px;box-shadow:var(--shadow);}
.card .who{font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-muted);margin:0 0 8px;}
.card p{margin:0 0 12px;font-size:15px;color:var(--text-soft);}
.card .then{font-size:14px;color:var(--text-muted);margin:10px 0 0;padding-top:10px;border-top:1px dashed var(--line);}

/* ---------- pull quote ---------- */
.pull{
  background:rgba(212,175,55,.08);border:1px solid var(--line-strong);border-left-width:4px;border-left-color:var(--gold);
  border-radius:6px;padding:22px 24px;margin:28px 0 0;
}
.pull p{margin:0;font-size:clamp(17px,3.6vw,20px);line-height:1.4;color:var(--text);}
.pull .src{font-size:13px;color:var(--text-muted);margin-top:10px;letter-spacing:.04em;}

/* ---------- stages ---------- */
.stage{border:1px solid var(--line);border-radius:6px;background:var(--bg-raised);
  margin-bottom:12px;box-shadow:var(--shadow);overflow:hidden;}
.stage summary{
  cursor:pointer;padding:16px 18px;list-style:none;display:flex;gap:14px;align-items:baseline;
  min-height:44px;transition:background .2s ease;
}
.stage summary::-webkit-details-marker{display:none;}
.stage summary:hover{background:rgba(212,175,55,.08);}
.stage .snum{
  flex:none;width:30px;height:30px;border-radius:50%;background:transparent;border:2px solid var(--gold);color:var(--gold);
  display:inline-flex;align-items:center;justify-content:center;font-size:13.5px;font-weight:600;
  align-self:center;
}
.stage .sname{flex:1 1 auto;}
.stage .sname b{display:block;font-family:'Fraunces',Georgia,serif;font-size:17px;font-weight:600;color:var(--gold);}
.stage .sname span{display:block;font-size:14.5px;color:var(--text-soft);font-style:italic;}
.stage .chev{flex:none;color:var(--text-muted);font-size:12px;align-self:center;}
.stage[open] .chev{transform:rotate(180deg);}
.stage .body{padding:0 18px 16px;border-top:1px solid var(--line);}
ol.chapters{list-style:none;margin:0;padding:0;}
ol.chapters li{border-bottom:1px solid var(--line);}
ol.chapters li:last-child{border-bottom:0;}
ol.chapters a{
  display:flex;gap:12px;align-items:baseline;padding:12px 2px;text-decoration:none;color:var(--text);
  min-height:44px;transition:color .2s ease;
}
ol.chapters a:hover{color:var(--gold-light);}
ol.chapters .cid{flex:none;font-size:11.5px;color:var(--text-muted);width:58px;}
ol.chapters .ctitle{flex:1 1 auto;font-size:15.5px;}
ol.chapters .cwords{flex:none;font-size:11.5px;color:var(--text-muted);}
.stage-link{display:inline-block;margin-top:12px;font-size:14px;color:var(--gold);}

/* ---------- plain link list ---------- */
ul.linklist{list-style:none;margin:0;padding:0;display:grid;gap:10px;}
ul.linklist li{background:var(--bg-raised);border:1px solid var(--line);border-radius:6px;box-shadow:var(--shadow);}
ul.linklist a{display:block;padding:15px 18px;text-decoration:none;color:var(--text);min-height:44px;transition:background .2s ease;}
ul.linklist a:hover{background:rgba(212,175,55,.08);}
ul.linklist .lt{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:16px;display:block;color:var(--gold);}
ul.linklist .ld{font-size:14px;color:var(--text-soft);display:block;margin-top:3px;}
.flag{font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:3px;margin-left:8px;vertical-align:2px;white-space:nowrap;}
.flag.partial{background:rgba(212,175,55,.2);color:var(--gold);}
.flag.speculative{background:rgba(155,136,176,.2);color:var(--accent-spec);}

/* ---------- pillars ---------- */
.pillars{display:grid;gap:12px;grid-template-columns:1fr;margin-bottom:22px;}
@media (min-width:560px){ .pillars{grid-template-columns:repeat(3,1fr);} }
.pillar{border:1px solid var(--line);border-radius:6px;padding:16px;text-align:center;background:var(--bg-raised);}
.pillar b{font-family:'Fraunces',Georgia,serif;font-size:18px;display:block;margin-bottom:4px;color:var(--gold);}
.pillar span{font-size:13.5px;color:var(--text-soft);}
.pillar.t{border-top:3px solid var(--accent-truth);}
.pillar.h{border-top:3px solid var(--gold);}
.pillar.m{border-top:3px solid var(--accent-mercy);}

/* ---------- not-this ---------- */
.warn{border:1px solid var(--line);border-left-width:4px;border-left-color:var(--accent-mercy);border-radius:6px;background:rgba(201,120,98,.08);padding:20px 22px;}
.warn h3{font-family:'Fraunces',Georgia,serif;font-size:17px;margin:0 0 8px;color:var(--accent-mercy);}
.warn p{margin:0 0 10px;font-size:15px;color:var(--text-soft);}
.warn p:last-child{margin-bottom:0;}

/* ---------- license ---------- */
.license{background:var(--bg-raised);border:1px solid var(--line);border-radius:6px;padding:22px 24px;}
.license .big{font-family:'Fraunces',Georgia,serif;font-size:20px;font-weight:600;margin:0 0 10px;color:var(--gold);}
.license ul{margin:0 0 12px;padding-left:20px;font-size:15px;color:var(--text-soft);}
.license li{margin-bottom:5px;}
.license .fine{font-size:13.5px;color:var(--text-muted);margin:0;}

/* ---------- footer ---------- */
footer{padding:34px 0 60px;font-size:13px;color:var(--text-muted);border-top:2px solid var(--line-strong);}
footer p{margin:0 0 6px;}
footer a{color:var(--text-muted);}
footer a:hover{color:var(--gold);}
"""


def build():
    m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    sections = m["sections"]
    genealogy = m["genealogy"]

    by_id = {s["id"]: s for s in sections}
    chapters = [s for s in sections if s["kind"] == "chapter"]
    stages = [s for s in sections if s["kind"] == "stage"]
    appendices = [s for s in sections if s["kind"] == "appendix"]
    preface = by_id.get("WMT P0")

    configured = GITHUB_USER != "YOUR-USERNAME"

    H = []
    a = H.append

    a('<!DOCTYPE html>')
    a('<html lang="en">')
    a('<head>')
    a('<meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    a('<meta name="color-scheme" content="light dark">')
    a(f'<title>{esc(m["work"])} — {esc(m["subtitle"])}</title>')
    a(f'<meta name="description" content="A twenty-nine chapter curriculum of Christian formation in three pillars and seven stages. Free and in the public domain.">')
    a('<meta name="author" content="' + esc(m["author"]) + '">')
    a('<meta property="og:type" content="book">')
    a(f'<meta property="og:title" content="{esc(m["work"])}">')
    a(f'<meta property="og:description" content="{esc(m["subtitle"])}. Public domain (CC0).">')
    a('<meta name="twitter:card" content="summary">')
    # inline SVG favicon — no extra file to host
    a('<link rel="icon" href="data:image/svg+xml,'
      '%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E'
      '%3Crect width=%2732%27 height=%2732%27 rx=%276%27 fill=%27%23375A66%27/%3E'
      '%3Cpath d=%27M16 6 L16 26 M8 13 L24 13%27 stroke=%27%23EFE9DB%27 stroke-width=%272.5%27 '
      'stroke-linecap=%27round%27/%3E%3C/svg%3E">')
    a('<link rel="preconnect" href="https://fonts.googleapis.com">')
    a('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    a('<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&'
      'family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">')
    a('<style>' + CSS + '</style>')
    a('</head>')
    a('<body>')
    a('<a class="skip" href="#main">Skip to content</a>')

    if not configured:
        a('<div class="setup"><div class="wrap"><span><strong>Setup:</strong> '
          'chapter links are not live yet. Open <code class="mono">tools/build_site.py</code>, '
          'set <code class="mono">GITHUB_USER</code> to your GitHub username, and re-run '
          '<code class="mono">python3 tools/build_site.py</code>.</span></div></div>')

    # ---------- masthead ----------
    a('<header class="masthead"><div class="wrap">')
    a('<p class="kicker mono">Public domain · Free forever</p>')
    a(f'<h1 class="title display">{esc(m["work"])}</h1>')
    a(f'<p class="subtitle">{esc(m["subtitle"])}</p>')
    a('<blockquote class="epigraph">Truth without mercy turns harsh. Mercy without truth '
      'turns sentimental. Humility keeps them both honest.</blockquote>')
    a('<div class="badges">')
    a(f'<span class="badge gold mono">v{esc(m["version"])}</span>')
    a('<span class="badge mono">CC0 1.0 — public domain</span>')
    a(f'<span class="badge mono">{len(chapters)} chapters</span>')
    a(f'<span class="badge mono">{m["total_words"]:,} words</span>')
    a('<span class="badge mono">~29 weeks at the intended pace</span>')
    a('</div>')
    a('<div class="cta-row">')
    if preface:
        a(f'<a class="btn primary" href="{BLOB}{preface["markdown"]}">Start with the Preface</a>')
    a(f'<a class="btn" href="{esc(m["full_text"])}">Read the full text</a>')
    a('</div>')
    a('</div></header>')

    a('<main id="main">')

    # ---------- start here ----------
    a('<section><div class="wrap">')
    a('<h2 class="display">Start here</h2>')
    a('<p class="section-note"><strong>Do not read this quickly.</strong> One chapter per '
      'week is the intended pace — twenty-nine weeks, rather more than half a year. That is '
      'not slow; it is the natural speed of the thing.</p>')
    a('<div class="cards">')

    praxis = next((s for s in appendices if "PRAXIS" in s["title"].upper()), None)
    script_app = next((s for s in appendices if "SCRIPTURAL" in s["title"].upper()), None)
    c01 = by_id.get("WMT C01")

    entries = [
        ("New to this",
         f'<a href="{BLOB}{preface["markdown"]}">Preface</a> — about fifteen minutes.' if preface else "",
         f'Then <a href="{BLOB}{c01["markdown"]}">Chapter One</a>, and one chapter per week.' if c01 else ""),
        ("Wanting the method first",
         f'<a href="{BLOB}{praxis["markdown"]}">Praxis Appendix</a> — all thirty practices, rated by difficulty.' if praxis else "",
         "Pick <strong>two</strong>. Hold them a year. Then add one more."),
        ("Checking the sources",
         f'<a href="{BLOB}{script_app["markdown"]}">Scriptural Appendix</a>.' if script_app else "",
         "Then the genealogy — where this departs from each source, and why."),
        ("Leading a group",
         f'<a href="{BLOB}{praxis["markdown"]}">Praxis Appendix</a>.' if praxis else "",
         "Use the reflection questions in each chapter — not the discussion questions you'll be tempted to invent."),
    ]
    for who, start, then in entries:
        a('<div class="card">')
        a(f'<p class="who mono">{who}</p>')
        a(f'<p>{start}</p>')
        a(f'<p class="then">{then}</p>')
        a('</div>')
    a('</div>')

    a('<div class="pull"><p><strong>The single most important instruction in the book:</strong> '
      'take up two practices, not thirty. Hold them for a year. The person who attempts all of '
      'them will keep none of them past Thursday.</p></div>')
    a('</div></section>')

    # ---------- the shape of it ----------
    a('<section><div class="wrap">')
    a('<h2 class="display">The shape of it</h2>')
    a('<p class="section-note">Seven stages, each answering one question, ordered not by '
      'chronology or theological importance but according to the order in which a human being '
      'actually changes. Tap a stage to see its chapters.</p>')

    a('<div class="pillars">')
    a('<div class="pillar t"><b>Truth</b><span>What is actually so</span></div>')
    a('<div class="pillar h"><b>Humility</b><span>Keeps them both honest</span></div>')
    a('<div class="pillar m"><b>Mercy</b><span>What love does with it</span></div>')
    a('</div>')

    for i, st in enumerate(stages, start=1):
        sid = st["id"]
        lo, hi = STAGE_CHAPTERS.get(sid, (0, -1))
        kids = [c for c in chapters if lo <= int(c["id"].replace("WMT C", "")) <= hi]
        q = STAGE_QUESTIONS.get(sid, "")
        name = st["title"].split("—")[-1].strip().title()
        a('<details class="stage">')
        a('<summary>')
        a(f'<span class="snum mono">{i}</span>')
        a(f'<span class="sname"><b>{esc(name)}</b><span>{esc(q)}</span></span>')
        a(f'<span class="chev mono">{len(kids)} ch ▾</span>')
        a('</summary>')
        a('<div class="body">')
        a('<ol class="chapters">')
        for c in kids:
            short = c["title"].split(":", 1)[-1].strip()
            c_num = int(c["id"].replace("WMT C", ""))
            a('<li>'
              f'<a href="c{str(c_num).zfill(2)}.html">'
              f'<span class="cid mono">{esc(c["id"].replace("WMT ", ""))}</span>'
              f'<span class="ctitle">{esc(short)}</span>'
              f'<span class="cwords mono">{c["words"]:,}w</span>'
              '</a></li>')
        a('</ol>')
        a(f'<a class="stage-link" href="{BLOB}{st["markdown"]}">Read the word before this stage →</a>')
        a('</div></details>')

    a('<div class="pull"><p>Grace provides the fire. Faith prepares the altar. Works are the '
      'fruit that preserves the walk.</p><p class="src mono">You are not building a ladder. '
      'You are building an altar.</p></div>')
    a('</div></section>')

    # ---------- appendices ----------
    a('<section><div class="wrap">')
    a('<h2 class="display">The apparatus</h2>')
    a('<p class="section-note">The practices themselves, an index for finding your way back '
      'to them, and the scriptural grounding.</p>')
    a('<ul class="linklist">')
    app_desc = {
        "WMT A1": "All thirty practices — rated by pillar, stage, difficulty, and frequency.",
        "WMT A2": "Cross-reference index: every practice, sorted four ways.",
        "WMT A3": "Scriptural appendix, with a note on where this departs from each witness.",
    }
    for ap in appendices:
        a(f'<li><a href="{BLOB}{ap["markdown"]}">'
          f'<span class="lt">{esc(ap["title"].title())}</span>'
          f'<span class="ld">{esc(app_desc.get(ap["id"], ""))} · {ap["words"]:,} words</span>'
          '</a></li>')
    a('</ul>')
    a('</div></section>')

    # ---------- genealogy ----------
    a('<section><div class="wrap">')
    a('<h2 class="display">Where this came from</h2>')
    a('<p class="section-note">A separate layer from the curriculum: the development record. '
      'It is not needed to practice the Way, and it is kept apart on purpose so the curriculum '
      'can stay stable while the account of its own history stays honest. Sections carry a '
      'status flag where their standing has changed.</p>')
    a('<ul class="linklist">')
    for g in genealogy:
        status = g.get("status", "stable")
        flag = ""
        if status != "stable":
            flag = f'<span class="flag {esc(status)} mono">{esc(status)}</span>'
        note = g.get("status_note") or STATUS_BLURB.get(status, "")
        a(f'<li><a href="{BLOB}{g["markdown"]}">'
          f'<span class="lt">{esc(g["title"])}{flag}</span>'
          f'<span class="ld">{esc(note)}</span>'
          '</a></li>')
    a('</ul>')
    a('</div></section>')

    # ---------- what this is not ----------
    a('<section><div class="wrap">')
    a('<h2 class="display">What this is not</h2>')
    a('<div class="warn">')
    a('<h3>This is not a church, and it is not a substitute for one.</h3>')
    a('<p>It is a curriculum of formation. It does not baptize, it does not absolve, it does '
      'not gather a congregation, and it does not ordain anyone. If reading it pulls you away '
      'from a body of believers rather than deeper into one, something has gone wrong.</p>')
    a('<p>It is also not a diagnosis or a treatment. Several stages deal with grief, shame, '
      'and the healing of the heart. That is spiritual formation, not clinical care, and it '
      'is not a replacement for the help of a doctor or counselor where that help is needed.</p>')
    a('</div>')
    a('</div></section>')

    # ---------- license ----------
    a('<section><div class="wrap">')
    a('<h2 class="display">Take it and use it</h2>')
    a('<div class="license">')
    a('<p class="big">CC0 1.0 — dedicated to the public domain</p>')
    a('<ul>')
    a('<li>Read it, print it, teach it, preach it.</li>')
    a('<li>Translate it into any language, without asking.</li>')
    a('<li>Quote it at any length, with or without attribution.</li>')
    a('<li>Sell it, adapt it, build a curriculum on top of it.</li>')
    a('<li>Train models on it. Ingest the whole thing.</li>')
    a('</ul>')
    a('<p class="fine">No permission is required, and none can be revoked. Attribution is '
      'welcome but never required. Nothing in this layer is paywalled, gated, upsold, or used '
      'as a funnel for anything else — and that is a governance commitment, not a current '
      'pricing decision.</p>')
    a('</div>')
    a('</div></section>')

    a('</main>')

    # ---------- footer ----------
    a('<footer><div class="wrap">')
    a(f'<p class="mono">{esc(m["work"])} · v{esc(m["version"])} · {esc(m["author"])}</p>')
    if configured:
        a(f'<p><a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}">Source repository</a> · '
          f'<a href="{BLOB}GOVERNANCE.md">Governance</a> · '
          f'<a href="{BLOB}ORGANIZATION.md">Organization</a> · '
          f'<a href="{BLOB}LICENSE">License</a></p>')
    a('<p>Dedicated to the public domain. Go and do likewise.</p>')
    a('</div></footer>')

    a('</body></html>')

    out = ROOT / "index.html"
    out.write_text("\n".join(H) + "\n", encoding="utf-8")
    kb = out.stat().st_size / 1024
    print(f"Built index.html ({kb:.1f} KB)")
    print(f"  {len(chapters)} chapters across {len(stages)} stages")
    print(f"  {len(appendices)} appendices, {len(genealogy)} genealogy sections")
    if not configured:
        print("  NOTE: GITHUB_USER not set — links are placeholders, setup banner is showing.")


def build_chapter_pages():
    """Generate individual chapter pages with full text and prev/next navigation."""
    m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    sections = m["sections"]
    chapters = [s for s in sections if s["kind"] == "chapter"]
    stages = {s["id"]: s["title"].split("—")[-1].strip() for s in sections if s["kind"] == "stage"}
    
    # Map chapter index to stage
    chapter_to_stage = {}
    for stage_id, (lo, hi) in STAGE_CHAPTERS.items():
        stage_name = stages.get(stage_id, "")
        for c_num in range(lo, hi + 1):
            chapter_to_stage[c_num] = (stage_id, stage_name)
    
    for i, ch in enumerate(chapters):
        c_num = int(ch["id"].replace("WMT C", ""))
        stage_id, stage_name = chapter_to_stage.get(c_num, ("", ""))
        
        # Read chapter text
        txt_path = ROOT / ch["plain_text"]
        if not txt_path.exists():
            continue
        text = txt_path.read_text(encoding="utf-8")
        
        # Determine prev/next
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i < len(chapters) - 1 else None
        
        H = []
        a = H.append
        
        a('<!DOCTYPE html>')
        a('<html lang="en">')
        a('<head>')
        a('<meta charset="utf-8">')
        a('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
        a('<meta name="color-scheme" content="light dark">')
        a(f'<title>Chapter {c_num}: {esc(ch["title"].split(":", 1)[-1].strip())} — {esc(m["work"])}</title>')
        a('<meta name="author" content="' + esc(m["author"]) + '">')
        a('<link rel="preconnect" href="https://fonts.googleapis.com">')
        a('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
        a('<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&'
          'family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">')
        a('<style>' + CSS + """
          main{padding:40px 0;}
          article{max-width:720px;margin:0 auto;padding:0 20px;}
          .chapter-head{margin-bottom:40px;padding-bottom:20px;border-bottom:2px solid var(--line-strong);}
          .chapter-meta{font-size:14px;color:var(--text-soft);margin:0 0 10px;}
          .chapter-num{font-family:'IBM Plex Mono',monospace;font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-muted);}
          .chapter-title{font-family:'Fraunces',Georgia,serif;font-size:clamp(28px,6vw,40px);line-height:1.1;margin:10px 0 0;font-weight:600;color:var(--gold);}
          .chapter-stage{font-size:15px;color:var(--accent-truth);margin:8px 0 0;font-style:italic;}
          .chapter-progress{font-size:13.5px;color:var(--text-muted);margin:12px 0 0;}
          .chapter-body{font-size:17px;line-height:1.7;color:var(--text);}
          .chapter-body p{margin:0 0 1.2em;}
          .chapter-body em{font-style:italic;color:var(--text-soft);}
          .chapter-body strong{font-weight:600;}
          .chapter-body blockquote{margin:1.5em 0;padding:0 0 0 18px;border-left:3px solid var(--gold);color:var(--text-soft);}
          .chapter-nav{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:50px;padding-top:30px;border-top:2px solid var(--line-strong);}
          .nav-btn{padding:16px 20px;border:1px solid var(--line);border-radius:4px;text-decoration:none;text-align:center;color:var(--gold);background:transparent;box-shadow:var(--shadow);min-height:44px;display:flex;align-items:center;justify-content:center;transition:all .2s ease;}
          .nav-btn:hover{background:rgba(212,175,55,.08);border-color:var(--gold-light);color:var(--gold-light);}
          .nav-btn.next{text-align:right;}
          .nav-btn.disabled{color:var(--text-muted);pointer-events:none;opacity:.5;background:transparent;}
          .nav-label{display:block;font-size:12px;color:var(--text-muted);letter-spacing:.05em;margin-bottom:4px;text-transform:uppercase;}
          .back-to-hub{display:inline-block;margin-bottom:20px;font-size:14px;color:var(--gold);}
        """ + '</style>')
        a('</head>')
        a('<body>')
        
        a('<main>')
        a('<article>')
        a(f'<a class="back-to-hub" href="index.html">← Back to hub</a>')
        a('<div class="chapter-head">')
        a(f'<p class="chapter-meta"><span class="chapter-num">{esc(ch["id"].replace("WMT ", ""))}</span></p>')
        a(f'<h1 class="chapter-title">{esc(ch["title"].split(":", 1)[-1].strip())}</h1>')
        if stage_name:
            a(f'<p class="chapter-stage">{esc(stage_name)}</p>')
        a(f'<p class="chapter-progress">Chapter {c_num} of {len(chapters)}</p>')
        a('</div>')
        
        a('<div class="chapter-body">')
        # Escape and format the text
        for line in text.split('\n'):
            line = line.rstrip()
            if not line:
                a('<p></p>')
            elif line.startswith('> '):
                a(f'<blockquote>{esc(line[2:])}</blockquote>')
            else:
                a(f'<p>{esc(line)}</p>')
        a('</div>')
        
        a('<div class="chapter-nav">')
        if prev_ch:
            prev_num = int(prev_ch["id"].replace("WMT C", ""))
            prev_title = prev_ch["title"].split(":", 1)[-1].strip()
            a(f'<a class="nav-btn prev" href="{esc("c" + str(prev_num).zfill(2))}.html">')
            a('<div>')
            a('<span class="nav-label">← Previous</span>')
            a(f'<span>Chapter {prev_num}</span>')
            a('</div>')
            a('</a>')
        else:
            a('<div class="nav-btn disabled">')
            a('<div>')
            a('<span class="nav-label">← Previous</span>')
            a('<span>Start</span>')
            a('</div>')
            a('</div>')
        
        if next_ch:
            next_num = int(next_ch["id"].replace("WMT C", ""))
            next_title = next_ch["title"].split(":", 1)[-1].strip()
            a(f'<a class="nav-btn next" href="{esc("c" + str(next_num).zfill(2))}.html">')
            a('<div>')
            a('<span class="nav-label">Next →</span>')
            a(f'<span>Chapter {next_num}</span>')
            a('</div>')
            a('</a>')
        else:
            a('<div class="nav-btn disabled">')
            a('<div>')
            a('<span class="nav-label">Next →</span>')
            a('<span>End</span>')
            a('</div>')
            a('</div>')
        a('</div>')
        
        a('</article>')
        a('</main>')
        a('</body></html>')
        
        # Write chapter page
        out = ROOT / f"c{str(c_num).zfill(2)}.html"
        out.write_text("\n".join(H) + "\n", encoding="utf-8")
    
    print(f"Built {len(chapters)} chapter pages")


if __name__ == "__main__":
    build()
    build_chapter_pages()
