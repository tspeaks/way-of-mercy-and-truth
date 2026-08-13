#!/usr/bin/env python3
"""
build_site.py — generates the static website for The Way of Mercy and Truth.

Reads manifest.json (produced by build.py) and the markdown in trunk/ and
genealogy/, so the site never drifts from the curriculum. Run build.py first.

    python3 tools/build.py
    python3 tools/build_site.py

Produces, at the repo root:
    index.html          the hub
    preface.html        front matter
    s1.html … s7.html   the seven stage introductions
    c01.html … c29.html the chapters
    a1.html … a3.html   the appendices
    g00.html … g09.html the genealogy
    404.html            not-found page
    CNAME, .nojekyll    GitHub Pages configuration

Every page is self-contained: no build step, no JavaScript required to read
anything. Arrow-key navigation is a progressive enhancement.

EDIT THESE if you rename the repo, change accounts, or change domain:
"""

import json
import re
from pathlib import Path

GITHUB_USER = "tspeaks"
GITHUB_REPO = "way-of-mercy-and-truth"
GITHUB_BRANCH = "main"
CUSTOM_DOMAIN = "wayofmercyandtruth.org"   # set to "" to disable the CNAME file

ROOT = Path(__file__).resolve().parent.parent
BLOB = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/"
REPO_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"

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

APPENDIX_BLURB = {
    "WMT A1": "All thirty practices — rated by pillar, stage, difficulty, and frequency.",
    "WMT A2": "Cross-reference index: every practice, sorted four ways.",
    "WMT A3": "Scriptural appendix, with a note on where this departs from each witness.",
}

# A line of scripture looks like: "<text> — <Book> <chapter>:<verse>"
SCRIPTURE_RE = re.compile(
    r"^(.{10,}?)\s+—\s+((?:[1-3]\s)?[A-Z][A-Za-z]+\.?\s+\d+:\d+(?:[-–]\d+)?)\s*$"
)


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def slug_for(section):
    """Stable output filename for a manifest section."""
    sid = section["id"]
    if sid == "WMT P0":
        return "preface.html"
    if sid.startswith("WMT S"):
        return f"s{sid[5:]}.html"
    if sid.startswith("WMT C"):
        return f"c{int(sid[5:]):02d}.html"
    if sid.startswith("WMT A"):
        return f"a{sid[5:]}.html"
    if sid.startswith("WMT G"):
        return f"g{int(sid[5:]):02d}.html"
    return sid.lower().replace(" ", "-") + ".html"


def render_markdown(md_text):
    """
    Render the narrow subset of markdown this corpus actually uses:
    headings (##, ###), paragraphs, and scripture citation lines.
    The leading H1 is dropped — the page template supplies the title.
    """
    body = md_text
    if body.startswith("---"):
        parts = body.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    out = []
    first_h1_dropped = False
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
            out.append(f"<h2>{esc(line[2:])}</h2>")
        else:
            m = SCRIPTURE_RE.match(line)
            if m:
                out.append(
                    '<blockquote class="scripture">'
                    f"<p>{esc(m.group(1))}</p>"
                    f"<cite>{esc(m.group(2))}</cite>"
                    "</blockquote>"
                )
            else:
                out.append(f"<p>{esc(line)}</p>")
    return "\n".join(out)


CSS = """
:root{
  --bg:#0C0B08; --bg-raised:#15140F;
  --gold:#C9A227; --gold-bright:#E3C158; --gold-pale:#EADFC4; --gold-dim:#8A7327;
  --text:#E4DCC6; --text-soft:#BFB49A; --text-muted:#8A8069;
  --truth:#7FA9B5; --mercy:#C4795F; --spec:#9C8AB2;
  --rule:rgba(201,162,39,0.22); --rule-strong:rgba(201,162,39,0.45);
  --shadow:0 1px 2px rgba(0,0,0,.5), 0 10px 30px rgba(0,0,0,.35);
}
*,*::before,*::after{box-sizing:border-box;}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;}
@media (prefers-reduced-motion: reduce){
  html{scroll-behavior:auto;}
  *,*::before,*::after{animation-duration:.01ms !important;transition-duration:.01ms !important;}
}
body{
  margin:0;
  color:var(--text);
  background-color:var(--bg);
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(201,162,39,.07), transparent 70%),
    radial-gradient(ellipse 60% 40% at 50% 110%, rgba(201,162,39,.05), transparent 70%);
  background-attachment:fixed;
  font-family:'Source Serif 4','Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif;
  font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
}
img{max-width:100%;height:auto;}
a{color:var(--gold);text-decoration-color:rgba(201,162,39,.45);text-underline-offset:3px;}
a:hover{color:var(--gold-bright);text-decoration-color:var(--gold-bright);}
:focus-visible{outline:2px solid var(--gold-bright);outline-offset:3px;}
.wrap{max-width:820px;margin:0 auto;padding:0 22px;}
.skip{position:absolute;left:-9999px;top:0;background:var(--bg-raised);color:var(--gold);
  padding:10px 16px;z-index:99;border:1px solid var(--rule-strong);}
.skip:focus{left:0;}
.mono{font-family:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;}
.display{font-family:'Cormorant Garamond','Iowan Old Style',Georgia,serif;font-weight:600;}

.rule-orn{display:flex;align-items:center;gap:14px;margin:0;color:var(--gold-dim);}
.rule-orn::before,.rule-orn::after{content:"";height:1px;flex:1;
  background:linear-gradient(90deg,transparent,var(--rule-strong),transparent);}
.rule-orn span{font-size:13px;letter-spacing:.3em;}

.setup{background:rgba(196,121,95,.14);border-bottom:1px solid var(--rule-strong);
  color:var(--gold-pale);font-size:14px;padding:10px 0;}
.setup .wrap{display:flex;gap:10px;flex-wrap:wrap;align-items:baseline;}
.setup code{background:rgba(201,162,39,.18);padding:1px 6px;font-size:13px;color:var(--gold-bright);}

/* ---------- masthead ---------- */
header.masthead{padding:62px 0 44px;text-align:center;}
header.masthead::after{content:"";display:block;height:1px;margin-top:38px;
  background:linear-gradient(90deg,transparent,var(--rule-strong) 20%,var(--rule-strong) 80%,transparent);}
.crest{width:64px;height:64px;margin:0 auto 22px;display:block;color:var(--gold);opacity:.92;}
.kicker{font-size:11.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--gold-dim);margin:0 0 16px;}
h1.title{font-size:clamp(34px,9vw,58px);line-height:1.04;margin:0 0 12px;color:var(--gold-pale);
  font-weight:600;letter-spacing:.005em;}
.subtitle{font-size:clamp(15px,3.4vw,18px);color:var(--text-soft);font-style:italic;
  margin:0 auto 30px;max-width:44ch;}
blockquote.epigraph{margin:0 auto 30px;padding:20px 24px;max-width:52ch;
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);
  font-size:clamp(15.5px,3.4vw,18px);color:var(--text-soft);line-height:1.5;font-style:italic;}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 28px;justify-content:center;}
.badge{font-size:11px;letter-spacing:.08em;padding:5px 11px;text-transform:uppercase;
  border:1px solid var(--rule);color:var(--text-muted);background:rgba(201,162,39,.05);white-space:nowrap;}
.badge.gold{border-color:var(--rule-strong);color:var(--gold);}
.cta-row{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;}
.btn{display:inline-block;padding:14px 26px;text-decoration:none;font-size:15px;font-weight:600;
  letter-spacing:.02em;border:1px solid var(--gold-dim);background:transparent;color:var(--gold);min-height:44px;}
.btn:hover{background:rgba(201,162,39,.1);border-color:var(--gold);color:var(--gold-bright);}
.btn.primary{background:var(--gold);border-color:var(--gold);color:#100E08;}
.btn.primary:hover{background:var(--gold-bright);border-color:var(--gold-bright);color:#100E08;}

section{padding:50px 0;}
section + section{border-top:1px solid var(--rule);}
h2.sec{font-size:clamp(23px,5vw,30px);margin:0 0 8px;color:var(--gold-pale);font-weight:600;}
.section-note{color:var(--text-soft);margin:0 0 26px;max-width:62ch;}

.cards{display:grid;gap:14px;grid-template-columns:1fr;}
@media (min-width:660px){ .cards{grid-template-columns:1fr 1fr;} }
.card{background:var(--bg-raised);border:1px solid var(--rule);padding:19px 21px;box-shadow:var(--shadow);}
.card .who{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold-dim);margin:0 0 9px;}
.card p{margin:0;font-size:15px;color:var(--text-soft);}
.card .then{font-size:14px;color:var(--text-muted);margin:11px 0 0;padding-top:11px;border-top:1px solid var(--rule);}

.pull{background:rgba(201,162,39,.06);border-top:2px solid var(--gold-dim);
  border-bottom:2px solid var(--gold-dim);padding:24px 26px;margin:30px 0 0;}
.pull p{margin:0;font-size:clamp(16.5px,3.5vw,19px);line-height:1.45;color:var(--gold-pale);}
.pull .src{font-size:13px;color:var(--text-muted);margin-top:12px;letter-spacing:.05em;font-style:italic;}

.pillars{display:grid;gap:12px;grid-template-columns:1fr;margin-bottom:26px;}
@media (min-width:560px){ .pillars{grid-template-columns:repeat(3,1fr);} }
.pillar{border:1px solid var(--rule);padding:18px 14px;text-align:center;background:var(--bg-raised);}
.pillar b{font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;display:block;
  margin-bottom:5px;color:var(--gold-pale);letter-spacing:.06em;}
.pillar span{font-size:13px;color:var(--text-muted);}
.pillar.t{border-top:2px solid var(--truth);}
.pillar.h{border-top:2px solid var(--gold);}
.pillar.m{border-top:2px solid var(--mercy);}

.stage{border:1px solid var(--rule);background:var(--bg-raised);margin-bottom:12px;box-shadow:var(--shadow);}
.stage summary{cursor:pointer;padding:17px 19px;list-style:none;display:flex;gap:15px;
  align-items:center;min-height:44px;}
.stage summary::-webkit-details-marker{display:none;}
.stage summary:hover{background:rgba(201,162,39,.06);}
.stage .snum{flex:none;width:34px;height:34px;border-radius:50%;background:transparent;
  border:1px solid var(--gold-dim);color:var(--gold);display:inline-flex;align-items:center;
  justify-content:center;font-size:14px;font-weight:600;}
.stage[open] .snum{background:var(--gold);color:#100E08;border-color:var(--gold);}
.stage .sname{flex:1 1 auto;}
.stage .sname b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;
  font-weight:600;color:var(--gold-pale);letter-spacing:.05em;}
.stage .sname span{display:block;font-size:14px;color:var(--text-soft);font-style:italic;}
.stage .chev{flex:none;color:var(--text-muted);font-size:11px;letter-spacing:.06em;}
.stage .body{padding:4px 19px 17px;border-top:1px solid var(--rule);}
ol.chapters{list-style:none;margin:0;padding:0;}
ol.chapters li + li{border-top:1px solid var(--rule);}
ol.chapters a{display:flex;gap:12px;align-items:baseline;padding:13px 2px;text-decoration:none;
  color:var(--text);min-height:44px;}
ol.chapters a:hover{color:var(--gold-bright);}
ol.chapters .cid{flex:none;font-size:11px;color:var(--text-muted);width:42px;}
ol.chapters .ctitle{flex:1 1 auto;font-size:15.5px;}
ol.chapters .cwords{flex:none;font-size:11px;color:var(--text-muted);}
.stage-link{display:inline-block;margin-top:14px;font-size:14px;}

ul.linklist{list-style:none;margin:0;padding:0;display:grid;gap:10px;}
ul.linklist li{background:var(--bg-raised);border:1px solid var(--rule);box-shadow:var(--shadow);}
ul.linklist a{display:block;padding:16px 19px;text-decoration:none;color:var(--text);min-height:44px;}
ul.linklist a:hover{background:rgba(201,162,39,.06);}
ul.linklist .lt{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;font-size:19px;
  display:block;color:var(--gold-pale);letter-spacing:.03em;}
ul.linklist .ld{font-size:14px;color:var(--text-soft);display:block;margin-top:4px;}
.flag{font-size:10px;letter-spacing:.1em;text-transform:uppercase;padding:2px 7px;margin-left:9px;
  vertical-align:2px;white-space:nowrap;border:1px solid;}
.flag.partial{border-color:var(--gold-dim);color:var(--gold);}
.flag.speculative{border-color:var(--spec);color:var(--spec);}

.warn{border:1px solid var(--rule);border-left:3px solid var(--mercy);
  background:rgba(196,121,95,.07);padding:22px 24px;}
.warn h3{font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;margin:0 0 10px;
  color:var(--mercy);letter-spacing:.02em;}
.warn p{margin:0 0 11px;font-size:15px;color:var(--text-soft);}
.warn p:last-child{margin-bottom:0;}
.license{background:var(--bg-raised);border:1px solid var(--rule);padding:24px 26px;}
.license .big{font-family:'Cormorant Garamond',Georgia,serif;font-size:24px;font-weight:600;
  margin:0 0 12px;color:var(--gold-pale);letter-spacing:.03em;}
.license ul{margin:0 0 14px;padding-left:20px;font-size:15px;color:var(--text-soft);}
.license li{margin-bottom:6px;}
.license .fine{font-size:13.5px;color:var(--text-muted);margin:0;}

footer{padding:36px 0 64px;font-size:13px;color:var(--text-muted);
  border-top:1px solid var(--rule);margin-top:20px;}
footer p{margin:0 0 7px;}
footer a{color:var(--text-muted);}
footer a:hover{color:var(--gold);}

/* ================= reading pages ================= */
.topbar{position:sticky;top:0;z-index:20;background:rgba(12,11,8,.94);
  border-bottom:1px solid var(--rule);}
@supports ((backdrop-filter:blur(8px)) or (-webkit-backdrop-filter:blur(8px))){
  .topbar{-webkit-backdrop-filter:saturate(140%) blur(8px);backdrop-filter:saturate(140%) blur(8px);}
}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;gap:14px;min-height:50px;}
.topbar a.home{font-size:13.5px;text-decoration:none;color:var(--gold);white-space:nowrap;}
.topbar .where{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--text-muted);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.progress{height:2px;}
.progress i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--gold-dim),var(--gold));}

article{max-width:680px;margin:0 auto;padding:44px 22px 0;}
.doc-head{margin-bottom:38px;padding-bottom:26px;border-bottom:1px solid var(--rule);text-align:center;}
.doc-kicker{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--gold-dim);margin:0 0 14px;}
.doc-title{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(30px,7vw,44px);
  line-height:1.1;margin:0;font-weight:600;color:var(--gold-pale);letter-spacing:.01em;}
.doc-sub{font-size:15px;color:var(--truth);margin:12px 0 0;font-style:italic;}
.doc-meta{font-size:12px;color:var(--text-muted);margin:14px 0 0;letter-spacing:.06em;}

.doc-body{font-size:18px;line-height:1.75;color:var(--text);}
.doc-body p{margin:0 0 1.25em;}
.doc-body > p:first-of-type::first-letter{float:left;font-family:'Cormorant Garamond',Georgia,serif;
  font-size:3.4em;line-height:.82;padding:.06em .1em 0 0;color:var(--gold);font-weight:600;}
.doc-body h2{font-family:'Cormorant Garamond',Georgia,serif;font-size:26px;font-weight:600;
  margin:2em 0 .7em;color:var(--gold-pale);letter-spacing:.03em;}
.doc-body h3{font-family:'Cormorant Garamond',Georgia,serif;font-size:22px;font-weight:600;
  margin:1.9em 0 .6em;color:var(--gold);letter-spacing:.03em;}
blockquote.scripture{margin:1.7em 0;padding:16px 0 16px 22px;border-left:2px solid var(--gold-dim);
  background:rgba(201,162,39,.04);}
blockquote.scripture p{margin:0;font-style:italic;color:var(--gold-pale);font-size:17px;line-height:1.6;}
blockquote.scripture cite{display:block;margin-top:9px;font-style:normal;font-size:12.5px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text-muted);}

.docnav{max-width:680px;margin:56px auto 0;padding:0 22px 70px;}
.docnav .orn{margin-bottom:26px;}
.navgrid{display:grid;grid-template-columns:1fr;gap:12px;}
@media (min-width:560px){ .navgrid{grid-template-columns:1fr 1fr;} }
.nav-btn{display:block;padding:17px 20px;border:1px solid var(--rule);text-decoration:none;
  background:var(--bg-raised);min-height:44px;}
.nav-btn:hover{background:rgba(201,162,39,.07);border-color:var(--gold-dim);}
.nav-btn .nav-label{display:block;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--gold-dim);margin-bottom:5px;}
.nav-btn .nav-title{display:block;font-size:15.5px;color:var(--text);line-height:1.3;}
.nav-btn:hover .nav-title{color:var(--gold-bright);}
.nav-btn.next{text-align:right;}
.nav-btn.disabled{opacity:.42;}
.nav-hub{text-align:center;margin-top:20px;font-size:13.5px;}
.kbd-hint{text-align:center;margin-top:14px;font-size:11.5px;color:var(--text-muted);letter-spacing:.05em;}
@media (hover:none){ .kbd-hint{display:none;} }

.notfound{text-align:center;padding:90px 22px;}
.notfound h1{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(30px,8vw,46px);
  color:var(--gold-pale);margin:0 0 14px;font-weight:600;}
.notfound p{color:var(--text-soft);max-width:44ch;margin:0 auto 26px;}

@media print{
  body{background:#fff;color:#000;}
  .topbar,.docnav,.skip,.setup,footer,.kbd-hint{display:none !important;}
  article{max-width:none;padding:0;}
  .doc-title,.doc-body h2,.doc-body h3{color:#000;}
  .doc-body{font-size:12pt;}
  blockquote.scripture{border-left:2px solid #999;background:none;}
  blockquote.scripture p{color:#222;}
  a{color:#000;text-decoration:none;}
}
"""

CREST_SVG = """<svg class="crest" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true">
<path d="M32 4 L54 12 V32 C54 45 43 55 32 60 C21 55 10 45 10 32 V12 Z" stroke-linejoin="round"/>
<path d="M32 18 V46 M22 27 H42" stroke-linecap="round" stroke-width="2.2"/>
<circle cx="32" cy="32" r="26" opacity=".35"/>
</svg>"""

KBD_JS = """<script>
(function(){
  var p=document.querySelector('[data-prev]'),n=document.querySelector('[data-next]');
  document.addEventListener('keydown',function(e){
    if(e.metaKey||e.ctrlKey||e.altKey)return;
    var t=e.target.tagName;if(t==='INPUT'||t==='TEXTAREA')return;
    if(e.key==='ArrowLeft'&&p)location.href=p.getAttribute('href');
    if(e.key==='ArrowRight'&&n)location.href=n.getAttribute('href');
  });
  var bar=document.querySelector('.progress i');
  if(bar){
    var upd=function(){
      var h=document.documentElement,m=(h.scrollHeight-h.clientHeight);
      bar.style.width=(m>0?(h.scrollTop/m*100):0)+'%';
    };
    addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd();
  }
})();
</script>"""


def head(title, description=""):
    L = []
    a = L.append
    a("<!DOCTYPE html>")
    a('<html lang="en">')
    a("<head>")
    a('<meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    a('<meta name="color-scheme" content="dark">')
    a('<meta name="theme-color" content="#0C0B08">')
    a(f"<title>{esc(title)}</title>")
    if description:
        a(f'<meta name="description" content="{esc(description)}">')
    a('<meta property="og:type" content="book">')
    a(f'<meta property="og:title" content="{esc(title)}">')
    if description:
        a(f'<meta property="og:description" content="{esc(description)}">')
    a('<meta name="twitter:card" content="summary">')
    a('<link rel="icon" href="data:image/svg+xml,'
      "%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E"
      "%3Crect width=%2732%27 height=%2732%27 fill=%27%230C0B08%27/%3E"
      "%3Cpath d=%27M16 6 L16 26 M9 13 H23%27 stroke=%27%23C9A227%27 stroke-width=%272.6%27 "
      'stroke-linecap=%27round%27/%3E%3C/svg%3E">')
    a('<link rel="preconnect" href="https://fonts.googleapis.com">')
    a('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    a('<link href="https://fonts.googleapis.com/css2?'
      "family=Cormorant+Garamond:wght@400;600&"
      "family=Source+Serif+4:ital,wght@0,400;0,600;1,400&"
      'family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">')
    a("<style>" + CSS + "</style>")
    a("</head>")
    a("<body>")
    a('<a class="skip" href="#main">Skip to content</a>')
    return L


def short_title(section):
    return section["title"].split(":", 1)[-1].strip()


def build_reading_order(m):
    """The sequence a reader actually walks, plus the genealogy sequence."""
    by_id = {s["id"]: s for s in m["sections"]}
    order = []
    if "WMT P0" in by_id:
        order.append(by_id["WMT P0"])
    for sid in ["WMT S1", "WMT S2", "WMT S3", "WMT S4", "WMT S5", "WMT S6", "WMT S7"]:
        if sid in by_id:
            order.append(by_id[sid])
            lo, hi = STAGE_CHAPTERS[sid]
            for n in range(lo, hi + 1):
                cid = f"WMT C{n:02d}"
                if cid in by_id:
                    order.append(by_id[cid])
    for s in m["sections"]:
        if s["kind"] == "appendix":
            order.append(s)
    return order, list(m["genealogy"])


def doc_page(section, prev_s, next_s, kicker, subtitle, meta, md_path, chapter_pos=None):
    """One reading page: sticky bar, rendered body, prev/next."""
    L = head(f"{short_title(section)} — The Way of Mercy and Truth")
    a = L.append

    a('<div class="topbar"><div class="wrap">')
    a('<a class="home" href="index.html">✦ The Way of Mercy and Truth</a>')
    a(f'<span class="where mono">{esc(meta)}</span>')
    a('</div><div class="progress"><i></i></div></div>')

    a('<main id="main">')
    a("<article>")
    a('<div class="doc-head">')
    a(f'<p class="doc-kicker">{esc(kicker)}</p>')
    a(f'<h1 class="doc-title">{esc(short_title(section))}</h1>')
    if subtitle:
        a(f'<p class="doc-sub">{esc(subtitle)}</p>')
    bits = [f'{section["words"]:,} words']
    if chapter_pos:
        bits.insert(0, chapter_pos)
    a(f'<p class="doc-meta mono">{esc(" · ".join(bits))}</p>')
    a("</div>")

    a('<div class="doc-body">')
    a(render_markdown((ROOT / md_path).read_text(encoding="utf-8")))
    a("</div>")
    a("</article>")

    a('<nav class="docnav" aria-label="Reading navigation">')
    a('<p class="rule-orn orn"><span>✦</span></p>')
    a('<div class="navgrid">')
    if prev_s:
        a(f'<a class="nav-btn prev" data-prev href="{slug_for(prev_s)}">'
          '<span class="nav-label">← Previous</span>'
          f'<span class="nav-title">{esc(short_title(prev_s))}</span></a>')
    else:
        a('<span class="nav-btn prev disabled"><span class="nav-label">← Previous</span>'
          '<span class="nav-title">The beginning</span></span>')
    if next_s:
        a(f'<a class="nav-btn next" data-next href="{slug_for(next_s)}">'
          '<span class="nav-label">Next →</span>'
          f'<span class="nav-title">{esc(short_title(next_s))}</span></a>')
    else:
        a('<span class="nav-btn next disabled"><span class="nav-label">Next →</span>'
          '<span class="nav-title">The end</span></span>')
    a("</div>")
    a('<p class="nav-hub"><a href="index.html">Return to the table of contents</a></p>')
    a('<p class="kbd-hint">Use ← and → to move between sections</p>')
    a("</nav>")
    a("</main>")
    a(KBD_JS)
    a("</body></html>")
    return "\n".join(L) + "\n"


def build():
    m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    sections = m["sections"]
    by_id = {s["id"]: s for s in sections}
    chapters = [s for s in sections if s["kind"] == "chapter"]
    stages = [s for s in sections if s["kind"] == "stage"]
    appendices = [s for s in sections if s["kind"] == "appendix"]
    preface = by_id.get("WMT P0")

    order, gen_order = build_reading_order(m)
    written = 0

    chapter_index = {c["id"]: i + 1 for i, c in enumerate(chapters)}
    stage_of_chapter = {}
    for sid, (lo, hi) in STAGE_CHAPTERS.items():
        for n in range(lo, hi + 1):
            stage_of_chapter[f"WMT C{n:02d}"] = sid

    for i, s in enumerate(order):
        prev_s = order[i - 1] if i > 0 else None
        next_s = order[i + 1] if i < len(order) - 1 else None
        sid = s["id"]
        pos = None
        if s["kind"] == "chapter":
            st_id = stage_of_chapter.get(sid, "")
            st = by_id.get(st_id)
            stage_name = st["title"].split("—")[-1].strip().title() if st else ""
            kicker = f'{sid.replace("WMT ", "")} · Stage {st_id[-1]}'
            subtitle = f'{stage_name} — {STAGE_QUESTIONS.get(st_id, "")}'
            pos = f"Chapter {chapter_index[sid]} of {len(chapters)}"
        elif s["kind"] == "stage":
            kicker = f"Stage {sid[-1]} of 7"
            subtitle = STAGE_QUESTIONS.get(sid, "")
        elif s["kind"] == "appendix":
            kicker = "Appendix"
            subtitle = APPENDIX_BLURB.get(sid, "")
        else:
            kicker = "Front matter"
            subtitle = ""
        (ROOT / slug_for(s)).write_text(
            doc_page(s, prev_s, next_s, kicker, subtitle, short_title(s), s["markdown"], pos),
            encoding="utf-8")
        written += 1

    for i, g in enumerate(gen_order):
        prev_s = gen_order[i - 1] if i > 0 else None
        next_s = gen_order[i + 1] if i < len(gen_order) - 1 else None
        status = g.get("status", "stable")
        sub = g.get("status_note") or (STATUS_BLURB.get(status, "") if status != "stable" else "")
        (ROOT / slug_for(g)).write_text(
            doc_page(g, prev_s, next_s, f'Genealogy · {g["id"].replace("WMT ", "")}',
                     sub, "Genealogy", g["markdown"]),
            encoding="utf-8")
        written += 1

    # ---------- hub ----------
    H = head(f'{m["work"]} — {m["subtitle"]}',
             "A twenty-nine chapter curriculum of Christian formation in three pillars "
             "and seven stages. Free and in the public domain.")
    a = H.append
    c01 = by_id.get("WMT C01")

    a('<header class="masthead"><div class="wrap">')
    a(CREST_SVG)
    a('<p class="kicker mono">Public domain · Free forever</p>')
    a(f'<h1 class="title display">{esc(m["work"])}</h1>')
    a(f'<p class="subtitle">{esc(m["subtitle"])}</p>')
    a('<blockquote class="epigraph">Truth without mercy turns harsh. Mercy without truth '
      "turns sentimental. Humility keeps them both honest.</blockquote>")
    a('<div class="badges">')
    a(f'<span class="badge gold mono">v{esc(m["version"])}</span>')
    a('<span class="badge mono">CC0 · public domain</span>')
    a(f'<span class="badge mono">{len(chapters)} chapters</span>')
    a(f'<span class="badge mono">{m["total_words"]:,} words</span>')
    a("</div>")
    a('<div class="cta-row">')
    if preface:
        a(f'<a class="btn primary" href="{slug_for(preface)}">Begin with the Preface</a>')
    if c01:
        a(f'<a class="btn" href="{slug_for(c01)}">Straight to Chapter One</a>')
    a("</div>")
    a("</div></header>")

    a('<main id="main"><div class="wrap">')

    a("<section>")
    a('<h2 class="sec display">Start here</h2>')
    a('<p class="section-note"><strong>Do not read this quickly.</strong> One chapter per '
      "week is the intended pace — twenty-nine weeks, rather more than half a year. That is "
      "not slow; it is the natural speed of the thing.</p>")
    a('<div class="cards">')
    praxis = next((s for s in appendices if "PRAXIS" in s["title"].upper()), None)
    script_app = next((s for s in appendices if "SCRIPTURAL" in s["title"].upper()), None)
    entries = [
        ("New to this",
         f'<a href="{slug_for(preface)}">The Preface</a> — about fifteen minutes.' if preface else "",
         f'Then <a href="{slug_for(c01)}">Chapter One</a>, and one chapter per week.' if c01 else ""),
        ("Wanting the method first",
         f'<a href="{slug_for(praxis)}">The Praxis Appendix</a> — all thirty practices, rated by difficulty.' if praxis else "",
         "Pick <strong>two</strong>. Hold them a year. Then add one more."),
        ("Checking the sources",
         f'<a href="{slug_for(script_app)}">The Scriptural Appendix</a>.' if script_app else "",
         f'Then <a href="{slug_for(gen_order[0])}">the genealogy</a> — where this departs from each source, and why.' if gen_order else ""),
        ("Leading a group",
         f'<a href="{slug_for(praxis)}">The Praxis Appendix</a>.' if praxis else "",
         "Use the reflection questions in each chapter — not the discussion questions "
         "you'll be tempted to invent."),
    ]
    for who, start, then in entries:
        a('<div class="card">')
        a(f'<p class="who mono">{who}</p>')
        a(f"<p>{start}</p>")
        a(f'<p class="then">{then}</p>')
        a("</div>")
    a("</div>")
    a('<div class="pull"><p><strong>The single most important instruction in the book:</strong> '
      "take up two practices, not thirty. Hold them for a year. The person who attempts all of "
      "them will keep none of them past Thursday.</p></div>")
    a("</section>")

    a("<section>")
    a('<h2 class="sec display">The shape of it</h2>')
    a('<p class="section-note">Seven stages, each answering one question, ordered not by '
      "chronology or theological importance but according to the order in which a human being "
      "actually changes. Open a stage to see its chapters.</p>")
    a('<div class="pillars">')
    a('<div class="pillar t"><b>Truth</b><span>What is actually so</span></div>')
    a('<div class="pillar h"><b>Humility</b><span>Keeps them both honest</span></div>')
    a('<div class="pillar m"><b>Mercy</b><span>What love does with it</span></div>')
    a("</div>")
    for i, st in enumerate(stages, start=1):
        sid = st["id"]
        lo, hi = STAGE_CHAPTERS.get(sid, (0, -1))
        kids = [c for c in chapters if lo <= int(c["id"].replace("WMT C", "")) <= hi]
        name = st["title"].split("—")[-1].strip().title()
        a('<details class="stage">')
        a("<summary>")
        a(f'<span class="snum mono">{i}</span>')
        a(f'<span class="sname"><b>{esc(name)}</b><span>{esc(STAGE_QUESTIONS.get(sid, ""))}</span></span>')
        a(f'<span class="chev mono">{len(kids)} ch</span>')
        a("</summary>")
        a('<div class="body"><ol class="chapters">')
        for c in kids:
            a("<li>"
              f'<a href="{slug_for(c)}">'
              f'<span class="cid mono">{esc(c["id"].replace("WMT ", ""))}</span>'
              f'<span class="ctitle">{esc(short_title(c))}</span>'
              f'<span class="cwords mono">{c["words"]:,}w</span>'
              "</a></li>")
        a("</ol>")
        a(f'<a class="stage-link" href="{slug_for(st)}">Read the word before this stage →</a>')
        a("</div></details>")
    a('<div class="pull"><p>Grace provides the fire. Faith prepares the altar. Works are the '
      'fruit that preserves the walk.</p><p class="src">You are not building a ladder. '
      "You are building an altar.</p></div>")
    a("</section>")

    a("<section>")
    a('<h2 class="sec display">The apparatus</h2>')
    a('<p class="section-note">The practices themselves, an index for finding your way back '
      "to them, and the scriptural grounding.</p>")
    a('<ul class="linklist">')
    for ap in appendices:
        a(f'<li><a href="{slug_for(ap)}">'
          f'<span class="lt">{esc(ap["title"].title())}</span>'
          f'<span class="ld">{esc(APPENDIX_BLURB.get(ap["id"], ""))} · {ap["words"]:,} words</span>'
          "</a></li>")
    a("</ul>")
    a("</section>")

    a("<section>")
    a('<h2 class="sec display">Where this came from</h2>')
    a('<p class="section-note">A separate layer from the curriculum: the development record. '
      "It is not needed to practice the Way, and it is kept apart on purpose so the curriculum "
      "can stay stable while the account of its own history stays honest. Sections carry a "
      "status flag where their standing has changed.</p>")
    a('<ul class="linklist">')
    for g in gen_order:
        status = g.get("status", "stable")
        flag = f'<span class="flag {esc(status)} mono">{esc(status)}</span>' if status != "stable" else ""
        note = g.get("status_note") or STATUS_BLURB.get(status, "")
        a(f'<li><a href="{slug_for(g)}">'
          f'<span class="lt">{esc(g["title"])}{flag}</span>'
          f'<span class="ld">{esc(note)}</span>'
          "</a></li>")
    a("</ul>")
    a("</section>")

    a("<section>")
    a('<h2 class="sec display">What this is not</h2>')
    a('<div class="warn">')
    a("<h3>This is not a church, and it is not a substitute for one.</h3>")
    a("<p>It is a curriculum of formation. It does not baptize, it does not absolve, it does "
      "not gather a congregation, and it does not ordain anyone. If reading it pulls you away "
      "from a body of believers rather than deeper into one, something has gone wrong.</p>")
    a("<p>It is also not a diagnosis or a treatment. Several stages deal with grief, shame, "
      "and the healing of the heart. That is spiritual formation, not clinical care, and it "
      "is not a replacement for the help of a doctor or counselor where that help is needed.</p>")
    a("</div>")
    a("</section>")

    a("<section>")
    a('<h2 class="sec display">Take it and use it</h2>')
    a('<div class="license">')
    a('<p class="big">CC0 1.0 — dedicated to the public domain</p>')
    a("<ul>")
    a("<li>Read it, print it, teach it, preach it.</li>")
    a("<li>Translate it into any language, without asking.</li>")
    a("<li>Quote it at any length, with or without attribution.</li>")
    a("<li>Sell it, adapt it, build a curriculum on top of it.</li>")
    a("<li>Train models on it. Ingest the whole thing.</li>")
    a("</ul>")
    a('<p class="fine">No permission is required, and none can be revoked. Attribution is '
      "welcome but never required. Nothing in this layer is paywalled, gated, upsold, or used "
      "as a funnel for anything else — and that is a governance commitment, not a current "
      "pricing decision.</p>")
    a("</div>")
    a(f'<p style="margin-top:22px;font-size:14px;"><a href="{esc(m["full_text"])}">'
      "Download the entire text as one plain-text file</a> · "
      f'<a href="{REPO_URL}">Source repository</a></p>')
    a("</section>")

    a("</div></main>")

    a('<footer><div class="wrap">')
    a(f'<p class="mono">{esc(m["work"])} · v{esc(m["version"])} · {esc(m["author"])}</p>')
    a(f'<p><a href="{REPO_URL}">Repository</a> · '
      f'<a href="{BLOB}GOVERNANCE.md">Governance</a> · '
      f'<a href="{BLOB}ORGANIZATION.md">Organization</a> · '
      f'<a href="{BLOB}LICENSE">License</a></p>')
    a("<p>Dedicated to the public domain. Go and do likewise.</p>")
    a("</div></footer>")
    a("</body></html>")

    (ROOT / "index.html").write_text("\n".join(H) + "\n", encoding="utf-8")

    F = head("Not found — The Way of Mercy and Truth")
    F.append('<main id="main"><div class="notfound">')
    F.append(CREST_SVG)
    F.append("<h1>That page is not here</h1>")
    F.append("<p>The road has twenty-nine chapters, seven stages, and a genealogy. "
             "This is none of them.</p>")
    F.append('<a class="btn primary" href="/">Return to the beginning</a>')
    F.append("</div></main></body></html>")
    (ROOT / "404.html").write_text("\n".join(F) + "\n", encoding="utf-8")

    if CUSTOM_DOMAIN:
        (ROOT / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

    print("Built index.html + 404.html")
    print(f"  {written} reading pages "
          f"(preface, {len(stages)} stages, {len(chapters)} chapters, "
          f"{len(appendices)} appendices, {len(gen_order)} genealogy)")
    if CUSTOM_DOMAIN:
        print(f"  CNAME -> {CUSTOM_DOMAIN}")
    print("  .nojekyll written")


if __name__ == "__main__":
    build()
