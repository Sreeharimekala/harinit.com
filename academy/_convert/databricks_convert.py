# -*- coding: utf-8 -*-
"""Rebuild the Databricks chapter pages in the AI & ML module-page layout.

Reads the original standalone chapter pages (academy/databricks/
databricks-chapter-N.html, as exported from the source docs) and rewrites
each one using the head, sidebar, document header, lesson sections and
module navigation of the AI & ML module pages, so all courses share one
look. The chapter content (cards, callouts, code blocks, tables, quizzes,
checklists) is kept as-is and styled to match the AI & ML dark theme.

Lesson ids (s5-1, s5-2, ...) are preserved, so databricks-course-data.js,
progress tracking and existing links keep working.

Usage (from the repo root):  python academy/_convert/databricks_convert.py
Pages already converted (they contain class="shell") are skipped, so it is
safe to run again after copying in fresh exports of individual chapters.
"""
import html
import os
import re

from bs4 import BeautifulSoup, Comment

BASE = os.path.dirname(os.path.abspath(__file__))
ACADEMY = os.path.dirname(BASE)
COURSE_DIR = os.path.join(ACADEMY, "databricks")
TEMPLATE = os.path.join(ACADEMY, "ai-ml", "Module_05_Statistics.html")
CHAPTERS = 24

# AI & ML blue palette -> Databricks orange palette (matches the course card).
PALETTE = [
    ("#5eb1ff", "#ff6b4a"), ("#7dc4ff", "#ff8a70"), ("#8b7cf6", "#ffb347"),
    ("94,177,255", "255,107,74"), ("#1a2430", "#2a1a16"), ("#1c2938", "#2e1f1a"),
]

EXTRA_CSS = """
/* Databricks chapter components, styled for the shared Academy theme */
.content code{font-family:var(--mono);font-size:.88em}
.content :not(pre)>code{background:var(--panel-2);border:1px solid var(--rule);padding:1px 6px;border-radius:4px;color:var(--ink);overflow-wrap:anywhere}
.content h3 .num{font-family:var(--mono);font-size:.68em;color:var(--accent);margin-right:10px;font-weight:600}
.content h5{font-family:var(--mono);font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin:18px 0 6px}
.code-wrap{position:relative}
.code-wrap pre.code{padding-top:36px}
.code-wrap .lang{position:absolute;top:14px;left:21px;z-index:2;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);max-width:calc(100% - 110px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.copy{position:absolute;top:10px;right:10px;z-index:2;font:500 11px var(--sans);color:var(--ink-dim);background:var(--panel-2);border:1px solid var(--rule);border-radius:5px;padding:3px 9px;cursor:pointer}
.copy:hover{color:var(--accent);border-color:var(--accent)}
.content .card p,.content .callout p,.content details p,.content td p,.content .next p,.content p.ref,.content p.section-intro{text-indent:0;padding-left:0}
.content .card ul,.content .card ol,.content .callout ul,.content .callout ol,.content details ul,.content details ol,.content .next ul,.content .next ol{padding-left:22px;margin-left:0}
.content p.ref{font-size:14px;color:var(--ink-faint)}
.content p.section-intro{font-size:16.5px;color:var(--ink)}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:12px 0 24px}
.card{border:1px solid var(--rule);border-radius:8px;padding:16px 18px;background:var(--panel)}
.content>.card{margin:12px 0 24px}
.content .card h4{margin-top:0;text-transform:none;letter-spacing:0;font-size:15.5px;color:var(--ink)}
.content .card>:last-child{margin-bottom:0}
.content .callout{background:#151b26;border:1px solid var(--rule);border-left:4px solid #7aa7f5;border-radius:0 8px 8px 0;padding:14px 18px;margin:18px 0 22px}
.content .callout .label{display:block;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#7aa7f5;margin-bottom:6px}
.content .callout.key{background:#14211a;border-left-color:#5fcf98}.content .callout.key .label{color:#5fcf98}
.content .callout.warn{background:#251f15;border-left-color:#e8b25a}.content .callout.warn .label{color:#e8b25a}
.content .callout>:last-child{margin-bottom:0}
.content td:first-child{font-weight:600;color:var(--ink)}
.content th{white-space:nowrap}
details.q{border:1px solid var(--rule);border-radius:8px;background:var(--panel);margin:10px 0;padding:0 16px}
details.q summary{cursor:pointer;padding:12px 0;font-weight:600;color:var(--ink);list-style:none;line-height:1.5}
details.q summary::-webkit-details-marker{display:none}
details.q summary::before{content:"+";display:inline-block;width:18px;color:var(--accent);font-weight:800}
details.q[open] summary::before{content:"\\2013"}
details.q .answer{padding:0 0 14px}
.content ol.steps{counter-reset:s;list-style:none;padding-left:0;margin-left:0}
.content ol.steps li{counter-increment:s;position:relative;padding:10px 0 10px 44px;border-bottom:1px dashed var(--rule)}
.content ol.steps li:last-child{border-bottom:none}
.content ol.steps li::before{content:counter(s);position:absolute;left:0;top:10px;width:28px;height:28px;border-radius:50%;background:var(--active-bg);color:var(--accent);font:700 13px var(--mono);display:grid;place-items:center}
.checklist label{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px dashed var(--rule);cursor:pointer;color:var(--ink-dim)}
.checklist label:last-of-type{border-bottom:none}
.checklist input{margin-top:6px;accent-color:var(--accent);width:16px;height:16px;flex:none}
.content .next{margin-top:48px;padding:22px 24px;border-radius:10px;background:var(--panel-2);border:1px solid var(--rule);border-left:4px solid var(--accent)}
.content .next h3{margin-top:0}
.lesson-extra{padding-top:64px;margin-top:-16px;border-top:1px solid var(--rule);scroll-margin-top:24px}
.lesson-extra .lesson-eyebrow{color:var(--ink-faint)}
"""

COPY_SCRIPT = """<script>document.querySelectorAll('pre.code').forEach(function(pre){var host=pre.parentElement.classList.contains('code-wrap')?pre.parentElement:pre;var b=document.createElement('button');b.type='button';b.className='copy';b.textContent='Copy';b.addEventListener('click',function(){var t=pre.innerText;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy';},1400);}).catch(function(){b.textContent='Select & copy';});});host.appendChild(b);});</script>"""


def esc(text):
    return html.escape(text, quote=False)


def load_template():
    src = open(TEMPLATE, encoding="utf-8").read()
    head_start = src[: src.index("<title>")]
    head_rest = src[src.index("</title>") + len("</title>"): src.index("</head>")]
    head_rest = re.sub(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/mathjax[^>]*></script>', "", head_rest)
    head_rest = head_rest.replace("../ai-ml-course-data.js", "../databricks-course-data.js")
    head_rest = head_rest.replace('<link rel="stylesheet" href="../academy-navigation.css">',
                                  "<style>" + EXTRA_CSS + '</style><link rel="stylesheet" href="../academy-navigation.css">')
    nav_style = re.search(r'<style>[^<]*\.module-nav[^<]*</style>(?=<nav class="module-nav">)', src).group(0)
    tail = src[src.index("</main></div>") + len("</main></div>"):]
    for old, new in PALETTE:
        head_start, head_rest, nav_style, tail = (s.replace(old, new) for s in (head_start, head_rest, nav_style, tail))
    return head_start, head_rest, nav_style, tail


def load_titles():
    data = open(os.path.join(ACADEMY, "databricks-course-data.js"), encoding="utf-8").read()
    return {int(n): t for n, t in re.findall(r"number: (\d+), title: '([^']*)'", data)}


def heading_text(h2):
    h2 = BeautifulSoup(str(h2), "html.parser").h2
    for num in h2.select("span.num"):
        num.decompose()
    return h2.get_text(" ", strip=True)


def module_nav(n, titles):
    def link(cls, label, num):
        return (f'<a class="module-nav-link {cls}" href="databricks-chapter-{num}.html"><span class="mn-label">{label}</span>'
                f'<span class="mn-title">{esc(titles[num])}</span></a>')
    prev = link("prev", "← Previous", n - 1) if n > 1 else \
        '<span class="module-nav-link prev disabled"><span class="mn-label">← Previous</span><span class="mn-title">—</span></span>'
    nxt = link("next", "Next →", n + 1) if n < CHAPTERS else \
        '<a class="module-nav-link next" href="index.html"><span class="mn-label">Finish →</span><span class="mn-title">Course Home</span></a>'
    return f'<nav class="module-nav">{prev}<a class="module-nav-link home" href="index.html">☰<br>Course Home</a>{nxt}</nav>'


def convert(n, template, titles):
    path = os.path.join(COURSE_DIR, f"databricks-chapter-{n}.html")
    raw = open(path, encoding="utf-8").read()
    if 'class="shell"' in raw:
        return "skipped (already converted)"
    soup = BeautifulSoup(raw, "html.parser")
    content = soup.select_one("main .content")
    hero = content.select_one("section.hero")
    eyebrow = hero.select_one(".eyebrow").get_text(" ", strip=True)
    h1 = hero.h1.get_text(" ", strip=True)
    lead = hero.select_one("p.lead")
    lead_html = lead.decode_contents().strip() if lead else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"] if desc_tag else lead.get_text(" ", strip=True)

    # Split the chapter body into sections at each top-level h2.
    sections, intro = [], []
    for node in list(content.children):
        if isinstance(node, Comment) or node is hero or (getattr(node, "name", None) in ("nav", "footer")):
            continue
        if getattr(node, "name", None) == "h2":
            sections.append({"id": node.get("id", ""), "title": heading_text(node), "body": []})
        elif sections:
            sections[-1]["body"].append(node)
        else:
            intro.append(node)
    if "".join(str(x) for x in intro).strip():
        raise ValueError(f"chapter {n}: unexpected content before the first lesson")

    lesson_re = re.compile(rf"^s{n}-(\d+)$")
    lessons = [s for s in sections if lesson_re.match(s["id"])]
    nav_lessons, nav_extras, body = [], [], []
    for s in sections:
        inner = "".join(str(x) for x in s["body"]).strip()
        m = lesson_re.match(s["id"])
        if m:
            num = f"{n}.{m.group(1)}"
            nav_lessons.append(f'<a href="#{s["id"]}" class="nav-link"><span class="nav-num">{num}</span>{esc(s["title"])}</a>')
            body.append(f'<section class="lesson" id="{s["id"]}"><div class="lesson-head"><span class="lesson-eyebrow">'
                        f'Chapter {n} · Lesson {num}</span><h2>{esc(s["title"])}</h2></div><div class="content">{inner}</div></section>')
        else:
            nav_extras.append(f'<a href="#{s["id"]}" class="nav-link">{esc(s["title"])}</a>')
            body.append(f'<section class="lesson-extra" id="{s["id"]}"><div class="lesson-head"><span class="lesson-eyebrow">'
                        f'Chapter {n}</span><h2>{esc(s["title"])}</h2></div><div class="content">{inner}</div></section>')

    head_start, head_rest, nav_style, tail = template
    count = len(lessons)
    sidebar = (
        '<nav class="sidebar" id="sidebar"><div class="brand"><div>\n'
        '<div class="brand-kicker">Databricks — HarinIT Academy</div>\n'
        f'<div class="brand-title">{esc(h1)}</div>\n'
        f'<div class="brand-sub">Chapter {n} · {count} lessons</div></div>'
        '<button class="nav-toggle" id="navToggle" aria-label="Toggle course contents" aria-controls="sidebar" aria-expanded="false">☰ Course Contents</button></div>\n'
        '<div class="nav-group-label">Lessons</div>\n' + "\n".join(nav_lessons) + "\n"
        + (('<div class="nav-group-label">Practice &amp; Review</div>\n' + "\n".join(nav_extras) + "\n") if nav_extras else "")
        + "</nav>"
    )
    header = (
        f'<header class="doc-header"><div class="doc-kicker">{esc(eyebrow)}</div><h1>{esc(h1)}</h1>\n'
        f"<p>{lead_html}</p>\n"
        f'<div class="doc-meta"><span class="pill">{count} lessons</span><span class="pill">Databricks</span>'
        '<span class="pill">HarinIT Academy</span></div></header>'
    )
    page = (
        head_start
        + f"<title>{esc(titles[n])} — Chapter {n} | Databricks | HarinIT Academy</title>"
        + f'<meta name="description" content="{html.escape(description)}">'
        + '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        + '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
        + head_rest + "</head><body>\n"
        + '<div class="shell">' + sidebar + '<main id="top">\n' + header + "\n" + "\n".join(body)
        + nav_style + module_nav(n, titles) + "</main></div>" + COPY_SCRIPT + tail
    )
    open(path, "w", encoding="utf-8", newline="\n").write(page)
    return f"{count} lessons, {len(nav_extras)} extra sections"


def main():
    template = load_template()
    titles = load_titles()
    for n in range(1, CHAPTERS + 1):
        print(f"Chapter {n}: {convert(n, template, titles)}")


if __name__ == "__main__":
    main()
