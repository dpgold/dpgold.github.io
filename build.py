"""Render index.html from data/*.json.  Run:  py build.py"""
import html, json, pathlib
from collections import defaultdict

VERSION = "1.0.1"
UPDATED = "November 2026"

ROOT = pathlib.Path(__file__).parent
load = lambda n: json.loads((ROOT / "data" / n).read_text(encoding="utf-8"))
P, PUBS, OPEDS, POSTS = load("profile.json"), load("publications.json"), load("opeds.json"), load("linkedin.json")
e = lambda s: html.escape(str(s), quote=True)

THEMES = {"aging": "Aging & longevity", "drugs": "Drug pricing & insurance design",
          "value": "Innovation & value", "access": "Disparities & access"}
TOP_JOURNALS = {"JAMA", "New England Journal of Medicine", "The Lancet", "BMJ", "Annals of Internal Medicine",
                "Proceedings of the National Academy of Sciences", "Quarterly Journal of Economics",
                "American Economic Review", "Journal of Economic Perspectives", "Health Affairs"}


def link(url, text, cls=""):
    if not url:
        return e(text)
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{e(url)}" target="_blank" rel="noopener">{e(text)}</a>'


def author_html(a):
    # Bold Dana's name in author lists.
    s = e(a)
    for v in ("Goldman DP", "Goldman D"):
        if v in s:
            return s.replace(v, f"<strong>{v}</strong>", 1)
    return s


def hero():
    links = "".join(f'<a class="pill" href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in P["links"])
    stats = "".join(f'<div class="stat"><span class="n">{e(s["n"])}</span><span class="l">{e(s["label"])}</span></div>' for s in P["stats"])
    return f"""
<header class="hero" id="top">
  <img class="photo" src="{e(P['photo'])}" alt="Portrait of {e(P['name'])}" width="800" height="670">
  <div class="hero-text">
    <h1>{e(P['name'])}</h1>
    <p class="headline">{e(P['headline'])}</p>
    <p class="loc">{e(P['location'])} · <a href="mailto:{e(P['email'])}">{e(P['email'])}</a></p>
    <nav class="pills" aria-label="Profiles">{links}</nav>
  </div>
</header>
<div class="stats">{stats}</div>"""


def about():
    return '<section id="about"><h2>About</h2>' + "".join(f"<p>{e(p)}</p>" for p in P["about"]) + "</section>"


def experience():
    out = ['<section id="experience"><h2>Experience</h2><ol class="timeline">']
    for x in P["experience"]:
        roles = "".join(f'<li><span class="role">{e(r["title"])}</span><span class="dates">{e(r["dates"])}</span></li>' for r in x["roles"])
        out.append(f'<li class="org"><h3>{e(x["org"])}</h3><ul class="roles">{roles}</ul></li>')
    out.append("</ol><h2 class='sub'>Education</h2><ul class='edu'>")
    for d in P["education"]:
        out.append(f'<li><span><strong>{e(d["school"])}</strong> — {e(d["degree"])}</span><span class="dates">{e(d["year"])}</span></li>')
    out.append("</ul></section>")
    return "".join(out)


def publications():
    pubs = sorted(PUBS, key=lambda p: -p["cites"])
    top5 = {p["doi"] for p in pubs[:5]}
    chips = '<button class="chip on" data-f="all">All</button>' + "".join(
        f'<button class="chip" data-f="{k}">{e(v)}</button>' for k, v in THEMES.items())
    items = []
    for p in pubs:
        badges = []
        if p["doi"] in top5:
            badges.append('<span class="badge cited">Most cited</span>')
        if p.get("key"):
            badges.append('<span class="badge key">Key paper</span>')
        cites = f'<span class="cites" title="Citations (OpenAlex)">{p["cites"]:,}</span>' if p["cites"] else '<span class="cites new">New</span>'
        items.append(f"""<li class="pub" data-theme="{p['theme']}" data-year="{p['year']}" data-cites="{p['cites']}">
  {cites}
  <div>
    <a class="pt" href="https://doi.org/{e(p['doi'])}" target="_blank" rel="noopener">{e(p['title'])}</a>
    <div class="pa">{author_html(p['authors'])}</div>
    <div class="pj"><em>{e(p['journal'])}</em> {e(p['cite'])} · {p['year']} <span class="tag">{e(THEMES[p['theme']])}</span> {''.join(badges)}</div>
  </div>
</li>""")
    books = "".join(
        f'<li><div class="pt">{link(b["url"], b["title"])}</div><div class="pa">{author_html(b["authors"])}</div><div class="pj"><em>{e(b["pub"])}</em> · {b["year"]}</div></li>'
        for b in P["books"])
    return f"""<section id="publications"><h2>Selected publications</h2>
<p class="lede">Greatest hits from 400+ articles — the most cited, the papers in top journals, and key recent work.
Complete list on <a href="https://scholar.google.com/citations?user=E3XmWfEAAAAJ&hl=en" target="_blank" rel="noopener">Google Scholar</a>
and <a href="https://orcid.org/0000-0001-8498-6396" target="_blank" rel="noopener">ORCID</a>.</p>
<div class="controls"><div class="chips" role="group" aria-label="Filter by theme">{chips}</div>
<label class="sort">Sort <select id="pubsort"><option value="cites">Most cited</option><option value="year">Newest</option></select></label></div>
<ol class="pubs" id="publist">{''.join(items)}</ol>
<p class="note">Citation counts from OpenAlex ({UPDATED}); Google Scholar counts run higher.</p>
<h2 class="sub">Books &amp; chapters</h2><ul class="pubs books">{books}</ul></section>"""


def opeds():
    by_year = defaultdict(list)
    for o in OPEDS:
        by_year[o["year"]].append(o)
    outlets = sorted({o["outlet"] for o in OPEDS})
    opts = '<option value="">All outlets</option>' + "".join(f'<option>{e(x)}</option>' for x in outlets)
    blocks = []
    for y in sorted(by_year, reverse=True):
        rows = "".join(
            f'<li data-outlet="{e(o["outlet"])}"><span class="outlet">{e(o["outlet"])}</span>'
            f'<span class="ot">{link(o["url"], o["title"])}<span class="oa">{e(o["authors"])} · {e(o["date"])}</span></span></li>'
            for o in by_year[y])
        blocks.append(f'<div class="year" data-year="{y}"><h3>{y}</h3><ul class="opeds">{rows}</ul></div>')
    n_out = len(outlets)
    return f"""<section id="opeds"><h2>Op-eds &amp; commentary</h2>
<p class="lede">{len(OPEDS)} pieces in {n_out} outlets, including the <em>New York Times</em>, <em>Wall Street Journal</em>,
<em>Washington Post</em>, <em>Los Angeles Times</em>, <em>STAT</em>, and <em>Health Affairs</em>.</p>
<div class="controls"><label class="sort">Outlet <select id="outlet">{opts}</select></label>
<input id="oq" type="search" placeholder="Search titles" aria-label="Search op-ed titles"></div>
{''.join(blocks)}</section>"""


def linkedin():
    if not POSTS:
        return ""
    posts = sorted(POSTS, key=lambda x: -x["impressions"])
    cards = "".join(
        f'<li class="post"><p>{e(x["text"])}</p><div class="pm"><strong>{x["impressions"]:,}</strong> impressions · '
        f'{x["reactions"]:,} reactions · {x["comments"]:,} comments<br>{e(x["date"])} · {link(x["url"], "View on LinkedIn →", "more")}</div></li>'
        for x in posts)
    return (f'<section id="linkedin"><h2>From LinkedIn</h2><p class="lede">Most-read posts of the past year, to 68,000+ followers. '
            f'More on <a href="https://www.linkedin.com/in/danapgoldman/recent-activity/all/" target="_blank" rel="noopener">LinkedIn</a>.</p>'
            f'<ul class="posts">{cards}</ul></section>')


def honors():
    h = "".join(f'<li><span class="dates">{e(y)}</span><span>{e(t)}</span></li>' for y, t in P["honors"])
    s = "".join(f'<li><span><strong>{e(r)}</strong> · {e(o)}</span><span class="dates">{e(d)}</span></li>' for r, o, d in P["service"])
    return f'<section id="honors"><h2>Honors</h2><ul class="honors">{h}</ul><h2 class="sub">Service &amp; advisory</h2><ul class="edu">{s}</ul></section>'


nav_items = [("about", "About"), ("experience", "Experience"), ("publications", "Publications"), ("opeds", "Op-eds")]
if POSTS:
    nav_items.append(("linkedin", "LinkedIn"))
nav_items.append(("honors", "Honors"))
nav = "".join(f'<a href="#{i}">{t}</a>' for i, t in nav_items)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(P['name'])}</title>
<meta name="description" content="{e(P['name'])} — health economist at USC. Selected publications, op-eds, and profile.">
<meta property="og:title" content="{e(P['name'])}">
<meta property="og:description" content="{e(P['headline'])}">
<meta property="og:image" content="https://dpgold.github.io/img/og.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v={VERSION}">
</head>
<body>
<nav class="top"><div class="wrap"><a class="brand" href="#top">{e(P['name'])}</a><div class="links">{nav}</div></div></nav>
<main class="wrap">
{hero()}
{about()}
{experience()}
{publications()}
{opeds()}
{linkedin()}
{honors()}
</main>
<footer class="wrap"><span>© {e(P['name'])}</span><span>Updated {UPDATED} · v{VERSION}</span></footer>
<script src="site.js?v={VERSION}"></script>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"index.html written: {len(PUBS)} publications, {len(OPEDS)} op-eds, {len(POSTS)} LinkedIn posts")
