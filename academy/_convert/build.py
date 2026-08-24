# -*- coding: utf-8 -*-
import json, re, os, html
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(BASE), "AI & ML")
OUT_DIR = os.path.join(os.path.dirname(BASE), "ai-ml")
os.makedirs(OUT_DIR, exist_ok=True)

with open(os.path.join(BASE, "curriculum.json"), encoding="utf-8") as f:
    CURRICULUM = json.load(f)

NUM_PREFIX_RE = re.compile(r"^\s*\d+(\.\d+)*\s*\.?\s*")

def normalize(text):
    text = text.replace("✓", "").strip()
    text = NUM_PREFIX_RE.sub("", text).strip()
    text = re.sub(r"\s+", " ", text)
    return text

def load_headings(path):
    htmldoc = open(path, encoding="utf-8").read()
    soup = BeautifulSoup(htmldoc, "html.parser")
    heads = soup.find_all(["h1", "h2"], class_="chapter-heading")
    return soup, heads

def match_module(mod):
    src_path = os.path.join(SRC_DIR, mod["source"])
    soup, heads = load_headings(src_path)
    norm_texts = [normalize(h.get_text(" ", strip=True)) for h in heads]
    expected = mod["lessons"]
    matches = []
    cursor = 0
    for exp in expected:
        exp_norm = exp.lower()
        best = None
        for i in range(cursor, len(heads)):
            if norm_texts[i].lower() == exp_norm:
                best = i
                break
        matches.append(best)
        if best is not None:
            cursor = best + 1
    return soup, heads, norm_texts, matches

def find_end_boundary(heads, norm_texts, matches, li, mod):
    if li < len(matches) - 1 and matches[li + 1] is not None:
        return matches[li + 1]
    last_idx = matches[li]
    first_title_norm = normalize(mod["lessons"][0]).lower()
    for i in range(last_idx + 1, len(heads)):
        if norm_texts[i].lower() == first_title_norm:
            return i
    return None

def collect_between(start_el, end_el):
    nodes = []
    node = start_el.next_sibling
    while node is not None:
        if end_el is not None and node is end_el:
            break
        nodes.append(node)
        node = node.next_sibling
    return "".join(str(n) for n in nodes)

# ---------- content transform ----------

STRAY_HEADING_RE = re.compile(r'<h[12] class="chapter-heading"[^>]*>(.*?)</h[12]>', re.DOTALL)
CODE_BLOCK_OPEN_RE = re.compile(r'<pre class="code-block"><code>')
CODE_BLOCK_CLOSE_RE = re.compile(r'</code></pre>')
DIAGRAM_OPEN_RE = re.compile(r'<pre class="diagram-block[^"]*">')
NUMBERED_P_RE = re.compile(r'<p class="numbered">\s*\d+\.\s*(.*?)</p>', re.DOTALL)

def transform_content(raw_html, lesson_title):
    s = raw_html
    # strip / demote any stray chapter-heading elements left inside content
    def _strip_heading(m):
        inner_text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        cleaned = normalize(inner_text)
        if cleaned.lower() == lesson_title.lower() or not cleaned:
            return ""
        return f"<p>{m.group(1)}</p>"
    s = STRAY_HEADING_RE.sub(_strip_heading, s)
    # code blocks -> Fabric pre.code
    s = CODE_BLOCK_OPEN_RE.sub('<pre class="code">', s)
    s = s.replace('<pre class="code">', '<pre class="code">')  # no-op safeguard
    s = CODE_BLOCK_CLOSE_RE.sub('</pre>', s)
    # diagram blocks -> Fabric pre.diagram
    s = DIAGRAM_OPEN_RE.sub('<pre class="diagram">', s)
    # numbered pseudo-headings -> h3
    s = NUMBERED_P_RE.sub(r'<h3>\1</h3>', s)
    # wrap bare tables
    s = s.replace('<table>', '<div class="table-wrap"><table>')
    s = s.replace('</table>', '</table></div>')
    s = s.strip()
    return s

PLACEHOLDER_NOTE = ('<div class="note"><b>Lesson focus:</b> This lesson is part of Module {num} '
                     '— {title}. Detailed lesson content can be added here from the corresponding '
                     'source material.</div>')
PLACEHOLDER_PROJECT = ('<div class="note"><b>Project brief:</b> This capstone project is part of '
                        'Module 12 — Capstone Projects. Detailed project instructions can be added here.</div>')

def extract_and_transform(mod):
    soup, heads, norm_texts, matches = match_module(mod)
    missing = [mod["lessons"][i] for i, m in enumerate(matches) if m is None]
    if missing:
        raise SystemExit(f"Module {mod['number']}: MISSING lessons {missing}")
    lessons_out = []
    for li, title in enumerate(mod["lessons"]):
        start_idx = matches[li]
        start_el = heads[start_idx]
        end_idx = find_end_boundary(heads, norm_texts, matches, li, mod)
        end_el = heads[end_idx] if end_idx is not None else None
        raw = collect_between(start_el, end_el)
        content = transform_content(raw, title)
        if len(re.sub(r'<[^>]+>', '', content).strip()) < 20:
            if mod["number"] == 12:
                content = PLACEHOLDER_PROJECT
            else:
                content = PLACEHOLDER_NOTE.format(num=mod["number"], title=mod["title"])
        lessons_out.append({"title": title, "content": content})
    return lessons_out

if __name__ == "__main__":
    report = []
    for mod in CURRICULUM["modules"]:
        lessons = extract_and_transform(mod)
        total_chars = sum(len(l["content"]) for l in lessons)
        placeholders = [l["title"] for l in lessons if "Detailed lesson content can be added" in l["content"] or "Detailed project instructions" in l["content"]]
        report.append(f"Module {mod['number']:>2} {mod['title']:<32} chars={total_chars:<8} placeholders={placeholders}")
        out_path = os.path.join(BASE, "out", f"module_{mod['number']}_transformed.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(lessons, f, ensure_ascii=False)
    print("\n".join(report))
