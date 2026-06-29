#!/usr/bin/env python3
"""Build a rich static website from the Telugu diet-plan Markdown files.

Output: site/  (index.html + one page per md file). Host free on GitHub Pages.
Browsers shape Telugu correctly, so no font workarounds are needed.
No third-party packages — a small Markdown renderer (with TABLE support) is built in.
"""
from pathlib import Path
import html as htmllib
import re

ROOT = Path(__file__).parent
MD_DIR = ROOT / "md"
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)

TITLES = {
    "menu-10-days": "📋 పూర్తి మెనూ (10 రోజులు)",
    "day-01": "🗓️ రోజు 1 — సోమవారం", "day-02": "🗓️ రోజు 2 — మంగళవారం",
    "day-03": "🗓️ రోజు 3 — బుధవారం", "day-04": "🗓️ రోజు 4 — గురువారం",
    "day-05": "🗓️ రోజు 5 — శుక్రవారం", "day-06": "🗓️ రోజు 6 — శనివారం",
    "day-07": "🗓️ రోజు 7 — ఆదివారం", "day-08": "🗓️ రోజు 8 — సోమవారం",
    "day-09": "🗓️ రోజు 9 — మంగళవారం", "day-10": "🗓️ రోజు 10 — బుధవారం",
    "day-11": "🗓️ రోజు 11 — గురువారం", "day-12": "🗓️ రోజు 12 — శుక్రవారం",
    "day-13": "🗓️ రోజు 13 — శనివారం", "day-14": "🗓️ రోజు 14 — ఆదివారం",
    "day-15": "🗓️ రోజు 15 — సోమవారం", "day-16": "🗓️ రోజు 16 — మంగళవారం",
    "day-17": "🗓️ రోజు 17 — బుధవారం", "day-18": "🗓️ రోజు 18 — గురువారం",
    "day-19": "🗓️ రోజు 19 — శుక్రవారం", "day-20": "🗓️ రోజు 20 — శనివారం",
    "day-21": "🗓️ రోజు 21 — ఆదివారం",
    "snacks-recipes": "🍪 స్నాక్ రెసిపీలు", "shopping-week-1": "🛒 షాపింగ్ — వారం 1",
    "shopping-week-2": "🛒 షాపింగ్ — వారం 2", "shopping-week-3": "🛒 షాపింగ్ — వారం 3",
    "nutrition-supplements": "🩺 పోషకాహారం & సప్లిమెంట్లు", "plan-summary": "📑 సారాంశం",
}
ORDER = list(TITLES.keys())

# day metadata for the home overview + badges
DAYS = [
    (1, "సోమ", "veg"), (2, "మంగళ", "nonveg"), (3, "బుధ", "nonveg"), (4, "గురు", "veg"),
    (5, "శుక్ర", "veg"), (6, "శని", "veg"), (7, "ఆది", "nonveg"), (8, "సోమ", "veg"),
    (9, "మంగళ", "nonveg"), (10, "బుధ", "nonveg"), (11, "గురు", "veg"), (12, "శుక్ర", "veg"),
    (13, "శని", "veg"), (14, "ఆది", "nonveg"), (15, "సోమ", "veg"), (16, "మంగళ", "nonveg"),
    (17, "బుధ", "nonveg"), (18, "గురు", "veg"), (19, "శుక్ర", "veg"), (20, "శని", "veg"),
    (21, "ఆది", "nonveg"),
]


def inline(text):
    text = htmllib.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def meal_class(title):
    t = title
    checks = [
        (("🎒", "స్కూల్"), "school"), (("✅", "రోజువారీ తప్పక"), "mustadd"),
        (("🩺", "డాక్టర్"), "doctor"), (("🛒", "షాపింగ్"), "shopping"),
        (("👩", "బ్యాచ్"), "prep"), (("🌅", "ఉదయం"), "morning"),
        (("🍛", "🍱", "లంచ్", "మధ్యాహ్నం భోజనం"), "lunch"), (("🌙", "రాత్రి"), "night"),
        (("స్నాక్", "చిరుతిండి", "తిండి"), "snack"),
    ]
    for keys, cls in checks:
        if any(k in t for k in keys):
            return cls
    return "generic"


# food "thumbnail" emoji per dish — colorful, reliable, no external images
DISH_EMOJI = [
    (("పెసరట్టు", "దోస", "అట్టు", "ఉత్తప్ప"), "🥞"),
    (("ఇడ్లీ", "గారె", "పునుగు"), "🍥"),
    (("చికెన్", "కోడి", "కీమా"), "🍗"), (("మటన్", "మాంసం"), "🍖"),
    (("చేప", "చేపల"), "🐟"), (("రొయ్య",), "🦐"),
    (("గుడ్డు", "ఎగ్", "భుర్జీ"), "🥚"), (("పనీర్", "పాలక్"), "🧀"),
    (("చపాతీ", "పుల్కా", "రోటీ"), "🫓"),
    (("ఉప్మా", "పొంగల్", "సేమియా", "ఆట్స్", "ఖిచిడీ"), "🍲"),
    (("పులావ్", "ఫ్రైడ్ రైస్", "పులిహోర"), "🍚"),
    (("సలాడ్", "సుండల్", "మొలక"), "🥗"),
    (("బిస్కెట్", "కుకీ"), "🍪"),
    (("చిక్కీ", "పల్లీ", "శనగ", "సున్ని", "నువ్వుల", "ఉండ", "లడ్డు", "అరిసె"), "🥜"),
    (("చిప్స్", "మిక్చర్", "జంతిక", "నిప్పట్", "చెక్క", "మరమర"), "🍘"),
    (("జావ", "పాలు", "మిల్క్", "మజ్జిగ"), "🥛"),
    (("పండు", "అరటి", "యాపిల్", "దానిమ్మ", "జామ", "బత్తాయి", "ఖర్జూర", "డ్రైఫ్రూట్", "చిలగడ"), "🍎"),
    (("అన్నం", "పప్పు", "పులుసు", "సాంబారు", "చారు", "రాజ్మా", "ఇగురు", "కూర", "సోయా"), "🍛"),
    (("స్కూల్",), "🎒"), (("షాపింగ్",), "🛒"), (("డాక్టర్", "పోషక"), "🩺"),
    (("తప్పక",), "✅"), (("బ్యాచ్", "రెసిపీ"), "👩‍🍳"),
]


def dish_emoji(title):
    for keys, e in DISH_EMOJI:
        if any(k in title for k in keys):
            return e
    return "🍽️"


def render_md(md):
    """Return (header_html, sections_html). Sections are grouped into cards."""
    lines = md.splitlines()
    blocks, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in s.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            blocks.append(("table", f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'))
            continue
        if line.startswith("## "):
            blocks.append(("h2", line[3:].strip())); i += 1
        elif line.startswith("# "):
            blocks.append(("h1", line[2:].strip())); i += 1
        elif line.startswith("> "):
            blocks.append(("quote", line[2:].strip())); i += 1
        elif line.startswith("---"):
            blocks.append(("hr", "")); i += 1
        elif line.startswith("**ప్రోటీన్:**"):
            blocks.append(("protein", line)); i += 1
        elif line.startswith("**చిట్కా:**"):
            blocks.append(("tip", line)); i += 1
        elif line.startswith("- "):
            items = []
            while i < n and lines[i].rstrip().startswith("- "):
                items.append(f"<li>{inline(lines[i].rstrip()[2:])}</li>"); i += 1
            blocks.append(("ul", "<ul>" + "".join(items) + "</ul>"))
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < n and re.match(r"^\d+\. ", lines[i].rstrip()):
                items.append(f"<li>{inline(re.sub(r'^\\d+\\. ', '', lines[i].rstrip()))}</li>"); i += 1
            blocks.append(("ol", '<ol class="steps">' + "".join(items) + "</ol>"))
        else:
            blocks.append(("p", line)); i += 1

    header_parts, sections, card, card_cls, started = [], [], [], "generic", False

    def el(kind, content):
        if kind == "table":
            return content
        if kind in ("ul", "ol"):
            return content
        if kind == "quote":
            cls = "callout warn" if "⚠️" in content else "callout"
            return f'<div class="{cls}">{inline(content)}</div>'
        if kind == "protein":
            val = inline(content.replace("**ప్రోటీన్:**", "").strip())
            return f'<div class="protein">💪 ప్రోటీన్: {val}</div>'
        if kind == "tip":
            val = inline(content.replace("**చిట్కా:**", "").strip())
            return f'<div class="tip">💡 {val}</div>'
        return f"<p>{inline(content)}</p>"

    def flush():
        nonlocal card, card_cls
        if card:
            sections.append(f'<section class="card meal-{card_cls}">' + "".join(card) + "</section>")
            card = []

    for kind, content in blocks:
        if kind == "h1":
            header_parts.append(("h1", content)); continue
        if kind == "h2":
            flush()
            started = True
            card_cls = meal_class(content)
            card.append(f'<h2 class="meal-head"><span class="thumb">{dish_emoji(content)}</span><span>{inline(content)}</span></h2>')
            continue
        if kind == "hr":
            flush(); started = False; continue
        if not started:
            # header zone (under h1): intro paragraph / meta line / quote
            if kind == "quote":
                header_parts.append(("intro", inline(content)))
            else:
                header_parts.append(("meta", el(kind, content)))
        else:
            card.append(el(kind, content))
    flush()
    return header_parts, "".join(sections)


def header_html(header_parts, stem):
    out = []
    for kind, content in header_parts:
        if kind == "h1":
            badge = ""
            if "నాన్‌వెజ్" in content:
                badge = '<span class="badge nonveg">🍗 నాన్‌వెజ్</span>'
            elif "వెజ్" in content:
                badge = '<span class="badge veg">🥬 వెజ్</span>'
            out.append(f'<h1>{inline(content)} {badge}</h1>')
        elif kind == "intro":
            out.append(f'<div class="intro">{content}</div>')
        else:
            out.append(f'<div class="meta">{content}</div>')
    return "".join(out)


CSS = """
:root{--green:#2e7d32;--green-d:#1b5e20;--orange:#ef6c00;--amber:#f9a825;--indigo:#5c6bc0;
--blue:#0277bd;--teal:#00897b;--pink:#d81b60;--bg:#eef2ea;--ink:#26332b;--card:#fff;}
*{box-sizing:border-box;}
body{margin:0;padding-bottom:60px;font-family:'Noto Sans Telugu','Poppins',system-ui,sans-serif;color:var(--ink);line-height:1.65;
background:linear-gradient(180deg,rgba(238,244,234,.92),rgba(231,238,240,.92)),
url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44'%3E%3Ccircle cx='22' cy='22' r='1.6' fill='%23bcd0b2'/%3E%3C/svg%3E");}
a{color:var(--green-d);}
.topbar{position:sticky;top:0;z-index:20;background:linear-gradient(90deg,var(--green-d),var(--green));
color:#fff;display:flex;align-items:center;gap:12px;padding:12px 16px;box-shadow:0 3px 12px rgba(0,0,0,.18);}
.topbar a.home{color:#fff;text-decoration:none;font-weight:700;background:rgba(255,255,255,.18);
padding:6px 12px;border-radius:20px;font-size:14px;}
.topbar .brand{font-weight:700;font-size:15px;letter-spacing:.2px;}
.page{max-width:860px;margin:0 auto;padding:16px 16px 80px;}
h1{font-size:23px;color:#fff;background:linear-gradient(120deg,var(--green),#43a047);
padding:16px 18px;border-radius:16px;margin:8px 0 12px;box-shadow:0 6px 18px rgba(46,125,50,.25);}
.intro{background:#f1f8e9;border-left:5px solid #7cb342;padding:12px 16px;border-radius:12px;margin:10px 0;font-size:15px;}
.meta{background:#fff;border:1px solid #e2e8dd;border-radius:12px;padding:10px 14px;margin:8px 0;font-size:14px;color:#445;}
.badge{display:inline-block;font-size:13px;font-weight:700;padding:3px 12px;border-radius:20px;vertical-align:middle;}
.badge.veg{background:#e8f5e9;color:#2e7d32;border:1px solid #a5d6a7;}
.badge.nonveg{background:#fff0ed;color:#d84315;border:1px solid #ffab91;}
/* meal cards */
.card{background:var(--card);border-radius:16px;padding:4px 16px 16px;margin:16px 0;
box-shadow:0 4px 16px rgba(20,40,25,.07);border:1px solid #eceee9;border-top:5px solid var(--green);}
.meal-head{display:flex;align-items:center;font-size:17px;font-weight:700;margin:14px 0 8px;padding:8px 12px;border-radius:12px;
background:#f4f7f1;color:var(--green-d);}
.thumb{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;
border-radius:50%;background:#fff;box-shadow:0 2px 7px rgba(0,0,0,.14);margin-right:11px;font-size:21px;}
.meal-morning{border-top-color:var(--orange);} .meal-morning .meal-head{background:#fff3e0;color:#e65100;}
.meal-lunch{border-top-color:var(--green);} .meal-lunch .meal-head{background:#eaf6ea;color:var(--green-d);}
.meal-snack{border-top-color:var(--amber);} .meal-snack .meal-head{background:#fff8e1;color:#f57f17;}
.meal-night{border-top-color:var(--indigo);} .meal-night .meal-head{background:#eceff8;color:#3949ab;}
.meal-school{border-top-color:var(--blue);} .meal-school .meal-head{background:#e1f5fe;color:#01579b;}
.meal-mustadd{border-top-color:var(--teal);} .meal-mustadd .meal-head{background:#e0f2f1;color:#00695c;}
.meal-doctor{border-top-color:var(--pink);} .meal-doctor .meal-head{background:#fce4ec;color:#ad1457;}
.meal-shopping{border-top-color:#6d4c41;} .meal-shopping .meal-head{background:#efebe9;color:#4e342e;}
.meal-prep{border-top-color:var(--teal);} .meal-prep .meal-head{background:#e0f2f1;color:#00695c;}
.card p{margin:6px 2px;} .card ul,.card ol{margin:6px 0;padding-left:24px;} li{margin:4px 0;}
strong{color:var(--green-d);} em{color:#6b7280;font-style:italic;}
.protein{display:inline-block;background:#ede7f6;color:#5e35b1;font-weight:600;font-size:13px;
padding:5px 12px;border-radius:20px;margin:6px 0;}
.tip{background:#fffde7;border-left:4px solid var(--amber);padding:8px 12px;border-radius:8px;margin:8px 0;font-size:14px;}
.steps{counter-reset:step;list-style:none;padding-left:0;}
.steps li{position:relative;padding:4px 0 4px 38px;margin:6px 0;}
.steps li::before{counter-increment:step;content:counter(step);position:absolute;left:0;top:2px;
width:26px;height:26px;background:var(--green);color:#fff;border-radius:50%;display:flex;
align-items:center;justify-content:center;font-size:13px;font-weight:700;}
.callout{background:#f1f8e9;border-left:5px solid #7cb342;padding:12px 14px;border-radius:10px;margin:14px 0;font-size:14px;}
.callout.warn{background:#fff8e1;border-left-color:#ffb300;}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0;border-radius:14px;
border:1px solid #e0e4da;box-shadow:0 3px 12px rgba(20,40,25,.06);}
table{border-collapse:collapse;width:100%;min-width:560px;background:var(--card);font-size:14px;}
th,td{border:1px solid #e8ece3;padding:9px 11px;text-align:left;vertical-align:top;}
thead th{position:sticky;top:0;background:linear-gradient(120deg,var(--green-d),var(--green));color:#fff;}
tr:nth-child(even) td{background:#f8faf6;}
/* home */
.hero{position:relative;overflow:hidden;color:#fff;border-radius:20px;padding:26px 22px;margin:10px 0 6px;
box-shadow:0 10px 26px rgba(46,125,50,.3);background:
url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Ccircle cx='32' cy='32' r='11' fill='none' stroke='%23ffffff' stroke-opacity='0.12' stroke-width='2'/%3E%3C/svg%3E"),
linear-gradient(135deg,#2e7d32,#66bb6a 70%,#9ccc65);}
.hero h1{background:none;padding:0;margin:0 0 8px;font-size:26px;box-shadow:none;}
.hero p{margin:4px 0;opacity:.96;font-size:14px;}
.section-title{font-size:16px;color:#33691e;margin:22px 6px 8px;font-weight:700;}
.week{display:flex;gap:8px;overflow-x:auto;padding:6px 2px 10px;}
.daychip{flex:0 0 auto;width:84px;text-decoration:none;background:#fff;border:1px solid #e3e7dd;
border-radius:14px;padding:10px 8px;text-align:center;box-shadow:0 2px 8px rgba(20,40,25,.06);}
.daychip .dn{font-size:20px;font-weight:800;color:var(--green-d);display:block;}
.daychip .wd{font-size:12px;color:#667;}
.daychip .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-top:6px;}
.dot.veg{background:#43a047;} .dot.nonveg{background:#e53935;}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin:12px 0;}
.tile{background:#fff;border:1px solid #e3e7dd;border-radius:16px;padding:16px;text-decoration:none;
color:var(--ink);box-shadow:0 3px 12px rgba(20,40,25,.07);transition:transform .08s,box-shadow .08s;display:block;}
.tile:active{transform:scale(.98);} .tile .ic{font-size:26px;display:block;margin-bottom:6px;}
.tile b{display:block;color:var(--green-d);font-size:15px;margin-bottom:2px;} .tile span{font-size:13px;color:#667;}
.tile.big{grid-column:1/-1;background:linear-gradient(120deg,#fffef8,#f1f8e9);}
/* day pills */
.pills{display:flex;gap:7px;overflow-x:auto;padding:10px 0 4px;margin-bottom:6px;}
.pills a{flex:0 0 auto;width:38px;height:38px;border-radius:50%;display:flex;align-items:center;
justify-content:center;text-decoration:none;font-weight:700;background:#fff;border:1px solid #d9e0d4;color:#557;}
.pills a.cur{background:var(--green);color:#fff;border-color:var(--green);}
.nav{display:flex;justify-content:space-between;gap:10px;margin-top:26px;}
.nav a{flex:1;background:#fff;border:1px solid #e3e7dd;border-radius:12px;padding:12px;text-decoration:none;
color:var(--green-d);font-weight:600;text-align:center;font-size:14px;box-shadow:0 2px 8px rgba(20,40,25,.05);}
.printbtn{position:fixed;right:16px;bottom:74px;z-index:30;background:var(--green);color:#fff;border:none;
border-radius:50%;width:52px;height:52px;font-size:22px;box-shadow:0 6px 16px rgba(0,0,0,.25);cursor:pointer;}
.tabbar{position:fixed;left:0;right:0;bottom:0;z-index:28;display:flex;background:rgba(255,255,255,.97);
backdrop-filter:blur(6px);border-top:1px solid #dbe2d5;box-shadow:0 -3px 12px rgba(0,0,0,.08);}
.tabbar a{flex:1;text-align:center;padding:7px 2px 8px;text-decoration:none;color:#6a766c;font-size:11px;font-weight:600;}
.tabbar a .ti{display:block;font-size:21px;line-height:1.2;}
.tabbar a.cur{color:var(--green);}
footer{max-width:860px;margin:0 auto;padding:0 16px 30px;color:#7a867d;font-size:12px;text-align:center;}
@media print{.topbar,.printbtn,.nav,.pills,.tabbar{display:none;}body{background:#fff;padding-bottom:0;}.card,.table-wrap{box-shadow:none;}}
"""

HEAD = """<!DOCTYPE html><html lang="te"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#2e7d32">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;500;600;700;800&family=Poppins:wght@500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="topbar"><a class="home" href="index.html">🏠 హోమ్</a><span class="brand">మా కుటుంబ ఆహార ప్రణాళిక</span></div>
"""

FOOT = """<button class="printbtn" onclick="window.print()" title="ప్రింట్">🖨️</button>
<footer>❤️ కుటుంబం కోసం · ఇది వైద్య సలహా కాదు — సందేహాలకు పిల్లల డాక్టర్‌ను సంప్రదించండి.</footer>
</body></html>"""


def day_pills(stem):
    if not stem.startswith("day-"):
        return ""
    cur = int(stem.split("-")[1])
    pills = "".join(
        f'<a href="day-{d:02d}.html" class="{"cur" if d==cur else ""}">{d}</a>' for d in range(1, 22)
    )
    return f'<div class="pills">{pills}</div>'


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


TABS = [
    ("index.html", "🏠", "హోమ్"), ("menu-10-days.html", "📋", "మెనూ"),
    ("snacks-recipes.html", "🍪", "రెసిపీలు"), ("shopping-week-1.html", "🛒", "షాపింగ్"),
    ("nutrition-supplements.html", "🩺", "ఆరోగ్యం"),
]


def tabbar(stem):
    def cur(href):
        page = href.split(".")[0]
        if stem == page:
            return "cur"
        if page == "shopping-week-1" and stem.startswith("shopping"):
            return "cur"
        return ""
    items = "".join(
        f'<a href="{h}" class="{cur(h)}"><span class="ti">{ic}</span><span>{t}</span></a>'
        for h, ic, t in TABS
    )
    return f'<nav class="tabbar">{items}</nav>'


def build_page(stem, md_text):
    header_parts, sections = render_md(md_text)
    title = TITLES.get(stem, "ఆహార ప్రణాళిక")
    body = day_pills(stem) + header_html(header_parts, stem) + sections + nav_links(stem)
    html = HEAD.format(title=title, css=CSS) + f'<main class="page">{body}</main>' + tabbar(stem) + FOOT
    (SITE / f"{stem}.html").write_text(html, encoding="utf-8")


def build_index():
    week = "".join(
        f'<a class="daychip" href="day-{d:02d}.html"><span class="dn">{d}</span>'
        f'<span class="wd">{wd}</span><br><span class="dot {tp}"></span></a>'
        for d, wd, tp in DAYS
    )
    body = f"""
<div class="hero"><h1>🍽️ మా కుటుంబ ఆహార ప్రణాళిక</h1>
<p>ఆంధ్ర శైలి · 21 రోజులు (3 వారాలు) · 4గురి కుటుంబం</p>
<p>ఉదయం &amp; రాత్రి టిఫిన్ · మధ్యాహ్నం అన్నం · పిల్లల స్కూల్ బాక్స్‌తో సహా</p></div>

<div class="section-title">🗓️ ఈ 21 రోజులు <span style="font-weight:500;color:#778;font-size:13px">(🟢 వెజ్ · 🔴 నాన్‌వెజ్)</span></div>
<div class="week">{week}</div>

<div class="cards">
<a class="tile big" href="menu-10-days.html"><span class="ic">📋</span><b>పూర్తి మెనూ (పట్టిక)</b>
<span>10 రోజుల భోజనం + స్కూల్ బాక్స్ + డాక్టర్ సూచనలు ఒకే చోట</span></a>
</div>

<div class="section-title">🍪 రెసిపీలు &amp; షాపింగ్</div>
<div class="cards">
<a class="tile" href="snacks-recipes.html"><span class="ic">🍪</span><b>స్నాక్ రెసిపీలు</b><span>14 ఇంటి స్నాక్స్</span></a>
<a class="tile" href="shopping-week-1.html"><span class="ic">🛒</span><b>షాపింగ్ 1</b><span>రోజు 1–5</span></a>
<a class="tile" href="shopping-week-2.html"><span class="ic">🛒</span><b>షాపింగ్ 2</b><span>రోజు 6–10</span></a>
<a class="tile" href="shopping-week-3.html"><span class="ic">🛒</span><b>షాపింగ్ 3</b><span>రోజు 11–21</span></a>
</div>

<div class="section-title">🩺 ఆరోగ్యం</div>
<div class="cards">
<a class="tile" href="nutrition-supplements.html"><span class="ic">🩺</span><b>పోషకాహారం</b><span>ప్రోటీన్, కాల్షియం, సప్లిమెంట్లు</span></a>
<a class="tile" href="plan-summary.html"><span class="ic">📑</span><b>సారాంశం</b><span>మొత్తం ఒక్క చూపులో</span></a>
</div>
"""
    html = HEAD.format(title="మా కుటుంబ ఆహార ప్రణాళిక", css=CSS) + f'<main class="page">{body}</main>' + tabbar("index") + FOOT
    (SITE / "index.html").write_text(html, encoding="utf-8")


def main():
    if not MD_DIR.exists():
        print("md/ not found"); return
    count = 0
    for md_path in sorted(MD_DIR.glob("*.md")):
        build_page(md_path.stem, md_path.read_text(encoding="utf-8"))
        count += 1
    build_index()
    print(f"✓ Built site/ with {count} pages + index.html")


if __name__ == "__main__":
    main()
