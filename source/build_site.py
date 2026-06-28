#!/usr/bin/env python3
"""Build a small static website from the Telugu diet-plan Markdown files.

Output: site/  (index.html + one page per md file).  Host it free on
Netlify / GitHub Pages / Cloudflare Pages, or open index.html directly.
Browsers shape Telugu correctly, so no font workarounds are needed here.
No third-party packages — a small Markdown renderer (with TABLE support) is built in.
"""
from pathlib import Path
import html as htmllib
import re
import sys

ROOT = Path(__file__).parent
MD_DIR = ROOT / "md"
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)

# Page order + nice Telugu titles -------------------------------------------
TITLES = {
    "menu-10-days": "📋 పూర్తి మెనూ (10 రోజులు)",
    "day-01": "🗓️ రోజు 1 — సోమవారం",
    "day-02": "🗓️ రోజు 2 — మంగళవారం",
    "day-03": "🗓️ రోజు 3 — బుధవారం",
    "day-04": "🗓️ రోజు 4 — గురువారం",
    "day-05": "🗓️ రోజు 5 — శుక్రవారం",
    "day-06": "🗓️ రోజు 6 — శనివారం",
    "day-07": "🗓️ రోజు 7 — ఆదివారం",
    "day-08": "🗓️ రోజు 8 — సోమవారం",
    "day-09": "🗓️ రోజు 9 — మంగళవారం",
    "day-10": "🗓️ రోజు 10 — బుధవారం",
    "snacks-recipes": "🍪 స్నాక్ రెసిపీలు",
    "shopping-week-1": "🛒 షాపింగ్ — వారం 1",
    "shopping-week-2": "🛒 షాపింగ్ — వారం 2",
    "nutrition-supplements": "🩺 పోషకాహారం & సప్లిమెంట్లు",
    "plan-summary": "📑 సారాంశం",
}
ORDER = list(TITLES.keys())


def inline(text):
    text = htmllib.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def render_md(md):
    lines = md.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            i += 1
            continue
        # Table: a "| ... |" row followed by a "|---|" separator row
        if s.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in s.strip("|").split("|")]
            i += 2  # skip header + separator
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            body = ""
            for r in rows:
                tds = "".join(f"<td>{inline(c)}</td>" for c in r)
                body += f"<tr>{tds}</tr>"
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        if line.startswith("## "):
            out.append(f"<h2>{inline(line[3:].strip())}</h2>")
            i += 1
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:].strip())}</h1>")
            i += 1
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:].strip())}</blockquote>")
            i += 1
        elif line.startswith("---"):
            out.append("<hr/>")
            i += 1
        elif line.startswith("- "):
            items = []
            while i < n and lines[i].rstrip().startswith("- "):
                items.append(f"<li>{inline(lines[i].rstrip()[2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < n and re.match(r"^\d+\. ", lines[i].rstrip()):
                items.append(f"<li>{inline(re.sub(r'^\\d+\\. ', '', lines[i].rstrip()))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
        else:
            out.append(f"<p>{inline(line)}</p>")
            i += 1
    return "".join(out)


CSS = """
:root{--green:#2e7d32;--green2:#66bb6a;--orange:#e65100;--bg:#f6f8f4;--card:#fff;}
*{box-sizing:border-box;}
body{margin:0;font-family:'Noto Sans Telugu',system-ui,sans-serif;background:var(--bg);color:#263238;line-height:1.6;}
.topbar{position:sticky;top:0;z-index:10;background:var(--green);color:#fff;display:flex;align-items:center;gap:14px;
  padding:12px 16px;box-shadow:0 2px 6px rgba(0,0,0,.15);}
.topbar a{color:#fff;text-decoration:none;font-weight:600;}
.topbar .brand{font-weight:700;font-size:15px;opacity:.95;}
.page{max-width:820px;margin:0 auto;padding:16px 16px 60px;}
h1{font-size:22px;color:#fff;background:var(--green);padding:14px 16px;border-radius:12px;margin:8px 0 14px;}
h2{font-size:17px;color:var(--orange);background:#fff3e0;border-left:5px solid #ffb74d;
  padding:10px 14px;border-radius:8px;margin:18px 0 8px;}
blockquote{background:#f1f8e9;border-left:5px solid var(--green2);margin:10px 0;padding:10px 14px;border-radius:8px;}
ul,ol{padding-left:24px;}li{margin:4px 0;}
strong{color:#33691e;}
hr{border:none;border-top:1px dashed #c5cabf;margin:18px 0;}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:12px 0;border-radius:10px;border:1px solid #e0e4da;}
table{border-collapse:collapse;width:100%;min-width:520px;background:var(--card);font-size:14px;}
th,td{border:1px solid #e3e7dd;padding:8px 10px;text-align:left;vertical-align:top;}
th{background:var(--green);color:#fff;font-weight:600;}
tr:nth-child(even) td{background:#fafbf8;}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin:14px 0;}
.card{background:var(--card);border:1px solid #e3e7dd;border-radius:12px;padding:14px;text-decoration:none;color:#263238;
  box-shadow:0 1px 3px rgba(0,0,0,.05);transition:transform .08s;}
.card:active{transform:scale(.98);}
.card b{display:block;color:var(--green);font-size:15px;}
.hero{background:linear-gradient(135deg,var(--green),var(--green2));color:#fff;border-radius:14px;padding:20px;margin:8px 0 6px;}
.hero h1{background:none;padding:0;margin:0 0 6px;font-size:24px;}
.hero p{margin:4px 0;opacity:.95;font-size:14px;}
.section-title{font-size:15px;color:#557;margin:20px 4px 6px;font-weight:700;}
.nav{display:flex;justify-content:space-between;gap:10px;margin-top:24px;}
.nav a{flex:1;background:var(--card);border:1px solid #e3e7dd;border-radius:10px;padding:10px;text-decoration:none;
  color:var(--green);font-weight:600;text-align:center;font-size:14px;}
footer{max-width:820px;margin:0 auto;padding:0 16px 40px;color:#789;font-size:12px;text-align:center;}
"""

HEAD = """<!DOCTYPE html><html lang="te"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="topbar"><a href="index.html">🏠 హోమ్</a><span class="brand">మా కుటుంబ ఆహార ప్రణాళిక</span></div>
"""

FOOT = """<footer>❤️ కుటుంబం కోసం · ఇది వైద్య సలహా కాదు — సందేహాలకు పిల్లల డాక్టర్‌ను సంప్రదించండి.</footer>
</body></html>"""


def nav_links(stem):
    if stem not in ORDER:
        return ""
    idx = ORDER.index(stem)
    parts = []
    if idx > 0:
        parts.append(f'<a href="{ORDER[idx-1]}.html">← {TITLES[ORDER[idx-1]].split(" ",1)[-1]}</a>')
    else:
        parts.append('<a href="index.html">← హోమ్</a>')
    if idx < len(ORDER) - 1:
        parts.append(f'<a href="{ORDER[idx+1]}.html">{TITLES[ORDER[idx+1]].split(" ",1)[-1]} →</a>')
    return f'<div class="nav">{"".join(parts)}</div>'


def build_page(stem, body):
    title = TITLES.get(stem, "ఆహార ప్రణాళిక")
    html = HEAD.format(title=title, css=CSS) + f'<main class="page">{body}{nav_links(stem)}</main>' + FOOT
    (SITE / f"{stem}.html").write_text(html, encoding="utf-8")


def build_index():
    days = "".join(
        f'<a class="card" href="day-{d:02d}.html"><b>రోజు {d}</b>{TITLES[f"day-{d:02d}"].split("—")[1].strip()}</a>'
        for d in range(1, 11)
    )
    body = f"""
<div class="hero"><h1>🍽️ మా కుటుంబ ఆహార ప్రణాళిక</h1>
<p>ఆంధ్ర శైలి · 10 రోజులు · నాన్న, అమ్మ, అమ్మాయి (9), అబ్బాయి (5)</p>
<p>ఉదయం & రాత్రి టిఫిన్ · మధ్యాహ్నం అన్నం · పిల్లల స్కూల్ బాక్స్‌తో సహా</p></div>

<a class="card" href="menu-10-days.html" style="display:block;margin:14px 0;"><b>📋 పూర్తి మెనూ (పట్టిక)</b>10 రోజుల భోజనం + స్కూల్ బాక్స్ + డాక్టర్ సూచనలు ఒకే చోట</a>

<div class="section-title">🗓️ రోజువారీ వివరాలు</div>
<div class="cards">{days}</div>

<div class="section-title">🍪 రెసిపీలు & షాపింగ్</div>
<div class="cards">
<a class="card" href="snacks-recipes.html"><b>🍪 స్నాక్ రెసిపీలు</b>14 ఇంటి స్నాక్స్</a>
<a class="card" href="shopping-week-1.html"><b>🛒 షాపింగ్ 1</b>రోజు 1–5</a>
<a class="card" href="shopping-week-2.html"><b>🛒 షాపింగ్ 2</b>రోజు 6–10</a>
</div>

<div class="section-title">🩺 ఆరోగ్యం</div>
<div class="cards">
<a class="card" href="nutrition-supplements.html"><b>🩺 పోషకాహారం</b>ప్రోటీన్, కాల్షియం, సప్లిమెంట్లు</a>
<a class="card" href="plan-summary.html"><b>📑 సారాంశం</b>మొత్తం ఒక్క చూపులో</a>
</div>
"""
    html = HEAD.format(title="మా కుటుంబ ఆహార ప్రణాళిక", css=CSS) + f'<main class="page">{body}</main>' + FOOT
    (SITE / "index.html").write_text(html, encoding="utf-8")


def main():
    if not MD_DIR.exists():
        print("md/ not found")
        return
    count = 0
    for md_path in sorted(MD_DIR.glob("*.md")):
        body = render_md(md_path.read_text(encoding="utf-8"))
        build_page(md_path.stem, body)
        count += 1
    build_index()
    print(f"✓ Built site/ with {count} pages + index.html")
    print(f"  Preview:  open {SITE/'index.html'}")


if __name__ == "__main__":
    main()
