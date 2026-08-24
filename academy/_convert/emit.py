# -*- coding: utf-8 -*-
"""Emit Fabric-template HTML files for the AI & ML course from the transformed JSON."""
import json, os, re, html

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(BASE), "ai-ml")
os.makedirs(OUT_DIR, exist_ok=True)

with open(os.path.join(BASE, "curriculum.json"), encoding="utf-8") as f:
    CURRICULUM = json.load(f)

MODULE_BLURBS = {
    1: "Core Python for AI/ML engineering — syntax, data structures, OOP, and the NumPy/Pandas foundations every later module builds on.",
    2: "SQL for data science — querying, aggregating, and cleaning data with the language every data platform speaks.",
    3: "The linear algebra, calculus, and probability that machine learning algorithms are built from.",
    4: "Data structures and algorithms for technical interviews and efficient, scalable code.",
    5: "Statistics for data-driven decisions — distributions, hypothesis testing, and the numbers behind machine learning.",
    6: "Cleaning, transforming, and visualizing data — the practical skills between raw data and a trained model.",
    7: "Classical machine learning end to end — algorithms, evaluation, ensembling, and shipping a trained model.",
    8: "Neural networks from first principles through CNNs, RNNs, and modern architectures in TensorFlow and PyTorch.",
    9: "Natural language processing — from tokenization through transformers, BERT, GPT, and building real NLP systems.",
    10: "MLOps and cloud — versioning, deploying, monitoring, and operating machine learning systems in production.",
    11: "Generative AI and large language models — transformers, RAG, agents, and building real GenAI applications.",
    12: "Ten end-to-end capstone projects applying the full curriculum to real-world AI/ML problems.",
}

HEAD_STYLE = """:root{
  --bg:#0f1115;--panel:#151822;--panel-2:#11141b;--ink:#e7e9ee;
  --ink-dim:#a7adba;--ink-faint:#6b7280;--accent:#5fd3c4;--accent-2:#f2a65a;
  --rule:#262b38;--code-bg:#0b0d12;--code-ink:#cde5ff;--diagram-ink:#7fe3c7;
  --table-head:#1b2030;--radius:10px;
  --serif:"Iowan Old Style","Palatino Linotype",Georgia,"Times New Roman",serif;
  --sans:"Inter","Segoe UI",system-ui,-apple-system,sans-serif;
  --mono:"Cascadia Mono","Cascadia Code","JetBrains Mono","Fira Code","SFMono-Regular",Consolas,"Liberation Mono",monospace;
}
*{box-sizing:border-box} html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.65;font-size:16px}
.shell{display:grid;grid-template-columns:300px 1fr;min-height:100vh}
.sidebar{position:sticky;top:0;height:100vh;overflow-y:auto;background:var(--panel-2);border-right:1px solid var(--rule);padding:28px 20px 40px}
.brand{display:flex;flex-direction:column;gap:4px;margin-bottom:26px;padding-bottom:20px;border-bottom:1px solid var(--rule)}
.brand-kicker{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.brand-title{font-family:var(--serif);font-size:22px;font-weight:600;color:var(--ink);line-height:1.25}
.brand-sub{font-size:12.5px;color:var(--ink-faint)}
.nav-group-label{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-faint);margin:18px 0 8px 4px}
.nav-link{display:flex;align-items:baseline;gap:10px;color:var(--ink-dim);text-decoration:none;font-size:14px;padding:8px 10px;border-radius:8px}
.nav-link:hover{background:rgba(95,211,196,.08);color:var(--ink)}
.nav-link.active{background:rgba(95,211,196,.12);color:var(--accent)}
.nav-num{font-family:var(--mono);font-size:11.5px;color:var(--accent-2);min-width:34px;flex-shrink:0}
main{padding:56px clamp(20px,6vw,90px) 120px;max-width:1050px}
.doc-header{margin-bottom:64px;padding-bottom:36px;border-bottom:1px solid var(--rule)}
.doc-kicker{font-family:var(--mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin-bottom:14px}
.doc-header h1{font-family:var(--serif);font-size:clamp(32px,5vw,48px);line-height:1.08;margin:0 0 18px;color:#fff}
.doc-header p{color:var(--ink-dim);font-size:16.5px;max-width:70ch;margin:0 0 22px}
.doc-meta{display:flex;flex-wrap:wrap;gap:10px}.pill{font-family:var(--mono);font-size:11.5px;color:var(--ink-dim);border:1px solid var(--rule);border-radius:999px;padding:5px 12px}
.lesson{padding-top:64px;margin-top:-16px;scroll-margin-top:24px}.lesson:first-of-type{padding-top:0}.lesson+.lesson{border-top:1px solid var(--rule)}
.lesson-head{margin-bottom:28px}.lesson-eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-2)}
.lesson-head h2{font-family:var(--serif);font-size:clamp(26px,4vw,36px);margin:8px 0 0;color:#fff;line-height:1.15}
.content h3{font-family:var(--serif);font-size:21px;color:#fff;margin:40px 0 12px;padding-top:4px;scroll-margin-top:24px;border-left:3px solid var(--accent);padding-left:14px}
.content h3:first-child{margin-top:0}
.content h4{font-family:var(--sans);font-size:13.5px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:var(--accent-2);margin:22px 0 8px}
.content p{color:var(--ink-dim);margin:0 0 14px;font-size:15.5px}.content strong{color:var(--ink)}
.content ul,.content ol{color:var(--ink-dim);margin:0 0 16px;padding-left:24px;font-size:15.5px}.content li{margin-bottom:6px}.content ul li::marker{color:var(--accent)}.content ol li::marker{color:var(--accent-2);font-family:var(--mono)}
pre.code{background:var(--code-bg);border:1px solid var(--rule);border-left:3px solid var(--accent);border-radius:var(--radius);padding:16px 18px;overflow-x:auto;margin:6px 0 20px;font-family:var(--mono);font-size:13.2px;line-height:1.6;color:var(--code-ink);white-space:pre}
pre.diagram{background:var(--code-bg);border:1px dashed var(--rule);border-radius:var(--radius);padding:20px 24px;overflow-x:auto;margin:8px 0 24px;font-family:var(--mono);font-size:13.5px;line-height:1.55;color:var(--diagram-ink);white-space:pre;tab-size:4}
.math-block{background:var(--code-bg);border:1px solid var(--rule);border-radius:var(--radius);padding:14px 18px;margin:8px 0 20px;overflow-x:auto;color:var(--code-ink)}
.table-wrap{overflow-x:auto;margin:8px 0 24px;border:1px solid var(--rule);border-radius:var(--radius)}
table{border-collapse:collapse;width:100%;font-size:14px}thead th{background:var(--table-head);color:#fff;text-align:left;font-weight:600;padding:10px 14px;border-bottom:1px solid var(--rule);white-space:nowrap}
tbody td{padding:9px 14px;color:var(--ink-dim);border-bottom:1px solid var(--rule);vertical-align:top}tbody tr:last-child td{border-bottom:none}tbody tr:hover td{background:rgba(255,255,255,.02);color:var(--ink)}
.callout{background:linear-gradient(180deg,rgba(95,211,196,.09),rgba(95,211,196,.03));border:1px solid rgba(95,211,196,.28);border-radius:14px;padding:20px 24px 8px;margin:26px 0 30px}
.note{background:rgba(242,166,90,.07);border:1px solid rgba(242,166,90,.25);border-radius:12px;padding:16px 20px;margin:20px 0;color:var(--ink-dim)}
.quote{border-left:3px solid var(--accent-2);padding:8px 16px;margin:18px 0;color:var(--ink)}
.top-link{display:inline-flex;align-items:center;gap:6px;margin-top:40px;font-family:var(--mono);font-size:12px;color:var(--ink-faint);text-decoration:none}.top-link:hover{color:var(--accent)}
.nav-toggle{display:none}
@media(max-width:900px){.shell{grid-template-columns:1fr}.sidebar{position:relative;height:auto;max-height:62px;overflow:hidden;transition:max-height .25s ease;padding:14px 16px}.sidebar.open{max-height:80vh;overflow-y:auto}.brand{margin-bottom:10px;padding-bottom:10px;flex-direction:row;align-items:flex-start;justify-content:space-between;border-bottom:none}.nav-toggle{display:inline-flex;background:var(--accent);color:#04211d;border:none;font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;padding:8px 12px;border-radius:8px;cursor:pointer;white-space:nowrap}main{padding:36px 20px 90px}}"""

def script_tags(needs_mathjax):
    tags = []
    if needs_mathjax:
        tags.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js" id="MathJax-script" async></script>')
    tags.append('<link rel="stylesheet" href="../academy-navigation.css">')
    tags.append('<script src="../academy-navigation.js" defer></script>')
    tags.append('<script src="../ai-ml-course-data.js" defer></script>')
    tags.append('<script src="../search-index.js" defer></script>')
    tags.append('<script src="../academy.js" defer></script>')
    return "".join(tags)

def sidebar_links(mod, num_prefix):
    out = []
    for i, title in enumerate(mod["lessons"], start=1):
        out.append(f'<a href="#lesson-{i}" class="nav-link"><span class="nav-num">{mod["number"]}.{i}</span>{html.escape(title)}</a>')
    return "\n".join(out)

def lesson_sections(mod, lessons):
    out = []
    for i, lesson in enumerate(lessons, start=1):
        out.append(
            f'<section class="lesson" id="lesson-{i}"><div class="lesson-head">'
            f'<span class="lesson-eyebrow">Module {mod["number"]} · Lesson {mod["number"]}.{i}</span>'
            f'<h2>{html.escape(lesson["title"])}</h2></div><div class="content">{lesson["content"]}</div></section>'
        )
    return "".join(out)

def build_module_html(mod, lessons):
    needs_mathjax = any("math-block" in l["content"] for l in lessons)
    count = len(mod["lessons"])
    blurb = MODULE_BLURBS[mod["number"]]
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{html.escape(mod["title"])} — Module {mod["number"]} | AI &amp; ML | HarinIT Academy</title><style>
{HEAD_STYLE}
</style>{script_tags(needs_mathjax)}</head><body>
<div class="shell"><nav class="sidebar" id="sidebar"><div class="brand"><div>
<div class="brand-kicker">AI &amp; ML — HarinIT Academy</div>
<div class="brand-title">{html.escape(mod["title"])}</div>
<div class="brand-sub">Module {mod["number"]} · {count} lessons</div></div><button class="nav-toggle" id="navToggle" aria-label="Toggle course contents" aria-controls="sidebar" aria-expanded="false">☰ Course Contents</button></div>
<div class="nav-group-label">Lessons</div>
{sidebar_links(mod, mod["number"])}
</nav><main id="top">
<header class="doc-header"><div class="doc-kicker">Module {mod["number"]}</div><h1>{html.escape(mod["title"])}</h1>
<p>{html.escape(blurb)}</p>
<div class="doc-meta"><span class="pill">{count} lessons</span><span class="pill">AI &amp; ML</span><span class="pill">HarinIT Academy</span></div></header>
{lesson_sections(mod, lessons)}
</main></div><script>document.getElementById("navToggle").addEventListener("click",()=>document.getElementById("sidebar").classList.toggle("open"));</script></body></html>
"""

if __name__ == "__main__":
    written = []
    for mod in CURRICULUM["modules"]:
        with open(os.path.join(BASE, "out", f"module_{mod['number']}_transformed.json"), encoding="utf-8") as f:
            lessons = json.load(f)
        htmldoc = build_module_html(mod, lessons)
        out_path = os.path.join(OUT_DIR, mod["file"])
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(htmldoc)
        written.append((mod["file"], len(htmldoc)))
    for name, size in written:
        print(f"{name}: {size:,} bytes")
