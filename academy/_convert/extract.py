# -*- coding: utf-8 -*-
import json, re, sys, os
from bs4 import BeautifulSoup, NavigableString, Tag

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(BASE), "AI & ML")
OUT_DIR = os.path.join(BASE, "out")
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
    html = open(path, encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
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
    """Return the heading index that bounds the end of lesson `li` (exclusive), or None for end-of-container."""
    if li < len(matches) - 1 and matches[li + 1] is not None:
        return matches[li + 1]
    # last lesson: look for a restart of lesson 0's title after this match, to cut off a trailing duplicate pass
    last_idx = matches[li]
    first_title_norm = normalize(mod["lessons"][0]).lower()
    for i in range(last_idx + 1, len(heads)):
        if norm_texts[i].lower() == first_title_norm:
            return i
    return None  # consume to end of container

def collect_between(start_el, end_el):
    """Collect a list of sibling-level nodes (Tags/NavigableStrings) starting right after start_el,
    up to (not including) end_el, by walking the flat document order and taking top-level nodes
    relative to start_el's parent chain. Uses next_elements + skip-descendants approach."""
    nodes = []
    node = start_el.next_sibling
    parent = start_el.parent
    while node is not None:
        if end_el is not None and node is end_el:
            break
        nodes.append(node)
        node = node.next_sibling
    return nodes

def extract_module(mod, report):
    soup, heads, norm_texts, matches = match_module(mod)
    missing = [mod["lessons"][i] for i, m in enumerate(matches) if m is None]
    if missing:
        report.append(f"Module {mod['number']}: MISSING {missing}")
        return None
    lessons_out = []
    for li, title in enumerate(mod["lessons"]):
        start_idx = matches[li]
        start_el = heads[start_idx]
        end_idx = find_end_boundary(heads, norm_texts, matches, li, mod)
        end_el = heads[end_idx] if end_idx is not None else None
        nodes = collect_between(start_el, end_el)
        # Serialize nodes to HTML string
        html_parts = []
        char_count = 0
        for n in nodes:
            s = str(n)
            html_parts.append(s)
            char_count += len(s)
        lessons_out.append({
            "title": title,
            "char_count": char_count,
            "html": "".join(html_parts),
        })
    total_chars = sum(l["char_count"] for l in lessons_out)
    empties = [l["title"] for l in lessons_out if l["char_count"] < 30]
    report.append(f"Module {mod['number']:>2} {mod['title']:<32} lessons={len(lessons_out):<3} total_chars={total_chars:<8} thin(<30chars)={empties}")
    return lessons_out

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "report"
    report = []
    all_out = {}
    for mod in CURRICULUM["modules"]:
        lessons_out = extract_module(mod, report)
        if lessons_out is not None:
            all_out[mod["number"]] = lessons_out
    print("\n".join(report))
    if mode == "write":
        for num, lessons in all_out.items():
            with open(os.path.join(OUT_DIR, f"module_{num}.json"), "w", encoding="utf-8") as f:
                json.dump(lessons, f, ensure_ascii=False)
        print("\nWrote", len(all_out), "module JSON files to", OUT_DIR)
