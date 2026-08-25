# -*- coding: utf-8 -*-
"""Rules 3, 2, 4, 6 (order matters: labels/headings first, then lists, then
questions, then the h3-run/adjacent-ul cleanup) -- DOM transforms applied
after merge_code.merge_runs has already repaired code blocks."""
import re
from bs4 import BeautifulSoup, NavigableString, Tag

NUM_LABEL_RE = re.compile(r'^\s*\d+(\.\d+)*\.?\s+(.*)$')
SECTION_RE = re.compile(r'^\s*Section\s+\d+\s*[–—-]\s*(.*)$', re.IGNORECASE)

STRAY_LABELS = {
    "answer", "example", "output", "input", "discuss", "solution", "summary",
    "conclusion", "takeaway", "takeaways", "recap", "note", "important",
    "warning", "tip", "hint", "explanation", "beginner", "intermediate",
    "advanced", "beginner / intermediate / advanced", "syntax", "question",
    "questions", "exercise", "exercises", "practice", "key takeaway",
    "key takeaways", "real-world application", "common mistake", "common mistakes",
}
STRAY_LABEL_NUM_RE = re.compile(
    r'^(example|mistake|answer|question|step|case|scenario|exercise|note|tip|solution|part)\s*\d*\s*$',
    re.IGNORECASE,
)
DIAGRAM_CHARS = set('│▼▲├└┌┬┼─→←↓↑╔╗╚╝║═╠╣╦╩╬')


def _first_child_text(tag):
    return tag.get_text().strip()


def rule3_labels_and_numbered(soup, container):
    """<p class="numbered">N. Title</p> or 'Section N - Title' -> <h3>Title</h3>;
    standalone one-word/short label <p> -> <h4>Label</h4>."""
    changed = 0
    for p in list(container.find_all('p', recursive=True)):
        # only operate on <p> that are direct content (not inside a pre/table/etc already handled)
        if p.find_parent(['pre', 'table']):
            continue
        text = _first_child_text(p)
        if not text:
            continue
        if SECTION_RE.match(text) or 'numbered' in (p.get('class') or []):
            # retag only -- keep every word, including the number/prefix,
            # verbatim (word-preservation takes priority over prefix style)
            h3 = soup.new_tag('h3')
            for child in list(p.contents):
                h3.append(child.extract())
            p.replace_with(h3)
            changed += 1
            continue
        low = text.lower().rstrip(':').strip()
        if (low in STRAY_LABELS or STRAY_LABEL_NUM_RE.match(low)) and len(text) <= 40:
            h4 = soup.new_tag('h4')
            for child in list(p.contents):
                h4.append(child.extract())
            p.replace_with(h4)
            changed += 1
    return changed


MID_SENTENCE_STOP_RE = re.compile(r'[.!?]\s+[A-Z]')
FLOW_CONNECTORS = (
    "however", "therefore", "thus", "this means", "this is", "these are",
    "that means", "as a result", "in this case", "in other words",
    "so ", "so,", "now ", "now,", "then ", "then,", "next,", "finally,",
    "let's", "let us", "we can", "we will", "you can", "you will",
    "notice that", "remember that", "keep in mind",
)


def is_list_itemish(p):
    """Short, single-clause, non-flow-continuation <p> that plausibly is one
    bullet in an enumerable list (objective/example/feature/mistake/question
    item) -- deliberately conservative so ordinary prose paragraphs are never
    swept into a <ul>."""
    if p.find_parent(['pre', 'table']):
        return False
    if p.get('class'):
        return False
    if p.find(['strong', 'em', 'a', 'code']) and len(p.get_text().strip()) > 90:
        # longer items with inline emphasis read more like prose sentences
        return False
    text = p.get_text().strip()
    if not text or len(text) > 140:
        return False
    if all(ch in DIAGRAM_CHARS or ch.isspace() for ch in text):
        return False  # arrow/box-drawing fragment -> belongs to rule 5, not a list
    if '  ' in text:
        return False  # multi-space column alignment -> ASCII table/plot, not prose
    alnum = sum(1 for ch in text if ch.isalnum())
    if alnum < 0.55 * len(text.replace(' ', '') or '1'):
        return False  # symbol/markup-dense fragment (garbage/JSON-ish), not a bullet
    if '{' in text and ':' in text and '"' in text:
        return False  # JSON-shaped embedded metadata, not a bullet
    words = text.split()
    if len(words) > 18:
        return False
    if text.endswith(':') and len(words) > 6:
        return False  # a longer colon-terminated sentence introduces a list, isn't one
    if MID_SENTENCE_STOP_RE.search(text):
        return False  # more than one sentence -> prose, not a bullet
    low = text.lower()
    if low.startswith(FLOW_CONNECTORS):
        return False
    return True


def rule2_listify(soup, container):
    """Convert runs of 3+ consecutive sibling <p> into <ul><li>, but only when
    they read as short, parallel, enumerable items -- never spanning a
    heading/table/pre, and never merging in a clearly-different final line
    (e.g. a much longer explanatory sentence right after short items)."""
    changed = 0
    node = container.contents[0] if container.contents else None
    while node is not None:
        nxt = node.next_sibling
        if isinstance(node, Tag) and node.name == 'p' and is_list_itemish(node):
            run = [node]
            cursor = node.next_sibling
            while cursor is not None:
                if isinstance(cursor, NavigableString):
                    if str(cursor).strip() == '':
                        cursor = cursor.next_sibling
                        continue
                    break
                if isinstance(cursor, Tag) and cursor.name == 'p' and is_list_itemish(cursor):
                    candidate_text = cursor.get_text().strip()
                    if len(run) >= 2:
                        # parallel-structure guard: once >=2 items agree on
                        # being questions, a non-question breaks the run
                        # (catches a trailing wrap-up tacked onto a question list)
                        run_is_questions = all(t.get_text().strip().endswith('?') for t in run)
                        if run_is_questions and not candidate_text.endswith('?'):
                            break
                        # outlier-length guard: a candidate much longer than
                        # the run's average reads as a lead-in/wrap-up
                        # sentence, not a parallel item -- stop before it
                        avg_words = sum(len(t.get_text().split()) for t in run) / len(run)
                        if len(candidate_text.split()) > max(6, avg_words * 1.7) and candidate_text.endswith('.'):
                            break
                    run.append(cursor)
                    cursor = cursor.next_sibling
                    continue
                break
            if len(run) >= 3:
                ul = soup.new_tag('ul')
                for item in run:
                    li = soup.new_tag('li')
                    # preserve inline markup (strong/em/code/a) inside the item
                    for child in list(item.contents):
                        li.append(child.extract())
                    ul.append(li)
                    ul.append(NavigableString('\n'))
                nxt = run[-1].next_sibling
                run[0].insert_before(ul)
                for item in run:
                    item.extract()
                changed += 1
        node = nxt
    return changed


QUESTION_RE = re.compile(r'\?\s*$')


def rule4_bold_questions(soup, container):
    changed = 0
    for p in container.find_all('p', recursive=True):
        if p.find_parent(['pre', 'table']):
            continue
        if p.find('strong') and len(p.get_text().strip()) == len((p.find('strong').get_text() or '').strip()):
            continue  # already fully bolded
        text = p.get_text().strip()
        if not text or len(text) > 200:
            continue
        if QUESTION_RE.search(text) and text.count('?') <= 2:
            # wrap the whole paragraph's inline content in <strong>
            strong = soup.new_tag('strong')
            for child in list(p.contents):
                strong.append(child.extract())
            p.append(strong)
            changed += 1
    return changed


ARROW_RE = re.compile(r'^[↓▼↑│┼]+$')


def _is_arrow_node(node):
    if not isinstance(node, Tag) or node.name not in ('p', 'pre'):
        return False
    txt = node.get_text().strip()
    return bool(txt) and bool(ARROW_RE.match(txt))


def _is_flow_step_candidate(node):
    if not isinstance(node, Tag) or node.name != 'p':
        return False
    if node.get('class'):
        return False
    if node.find_parent(['pre', 'table']):
        return False
    txt = node.get_text().strip()
    if not txt or len(txt) > 60 or len(txt.split()) > 6:
        return False
    if '  ' in txt:
        return False  # column-aligned fragment, not a single flow step
    alnum = sum(1 for ch in txt if ch.isalnum())
    if alnum < 0.6 * len(txt.replace(' ', '') or '1'):
        return False  # box-drawing/tree-diagram fragment, not plain step text
    if MID_SENTENCE_STOP_RE.search(txt) or txt.endswith(('.', '?', '!')):
        return False
    return True


def _next_tag(node):
    cursor = node.next_sibling
    while isinstance(cursor, NavigableString) and str(cursor).strip() == '':
        cursor = cursor.next_sibling
    return cursor


def rule5_flow_diagrams(soup, container):
    """A run of step, arrow, step, arrow, ... (only-arrow-character nodes
    strictly alternating with short plain-text step nodes) becomes a
    <div class="flow"> of bold centered steps joined by a short accent-colored
    line + small triangle -- pure sequential pipelines only, never 2D ASCII
    art (scatter plots, tables) which don't match this alternating shape."""
    changed = 0
    node = container.contents[0] if container.contents else None
    while node is not None:
        nxt = node.next_sibling
        if _is_flow_step_candidate(node) and _is_arrow_node(_next_tag(node)):
            steps = [node]
            arrow_node = _next_tag(node)
            cursor = arrow_node
            while _is_arrow_node(cursor):
                after_arrow = _next_tag(cursor)
                if not _is_flow_step_candidate(after_arrow):
                    break
                steps.append(after_arrow)
                cursor = _next_tag(after_arrow)
            if len(steps) >= 2:
                # collect every original node from first step through last step
                span = []
                walk = node
                while True:
                    span.append(walk)
                    if walk is steps[-1]:
                        break
                    walk = walk.next_sibling
                flow = soup.new_tag('div')
                flow['class'] = 'flow'
                for i, step in enumerate(steps):
                    if i > 0:
                        arrow_div = soup.new_tag('div')
                        arrow_div['class'] = 'flow-arrow'
                        arrow_div.string = '▼'
                        flow.append(arrow_div)
                        flow.append(NavigableString('\n'))
                    step_div = soup.new_tag('div')
                    step_div['class'] = 'flow-step'
                    for child in list(step.contents):
                        step_div.append(child.extract())
                    flow.append(step_div)
                    flow.append(NavigableString('\n'))
                nxt = span[-1].next_sibling
                span[0].insert_before(flow)
                for item in span:
                    item.extract()
                changed += 1
        node = nxt
    return changed


def flow_css(accent_var):
    return (
        ".flow{margin:22px 0;text-align:center}"
        ".flow-step{font-weight:700}"
        f".flow-arrow{{color:var({accent_var});font-size:13px;line-height:1;margin:6px 0 2px;position:relative}}"
        f".flow-arrow::before{{content:'';display:block;width:2px;height:9px;margin:0 auto 2px;background:var({accent_var})}}"
    )


def rule6_h3_runs_and_adjacent_uls(soup, container):
    changed = 0
    # (a) merge adjacent single-item <ul> into one list
    node = container.contents[0] if container.contents else None
    while node is not None:
        nxt = node.next_sibling
        if isinstance(node, Tag) and node.name == 'ul':
            run = [node]
            cursor = node.next_sibling
            while cursor is not None:
                if isinstance(cursor, NavigableString):
                    if str(cursor).strip() == '':
                        cursor = cursor.next_sibling
                        continue
                    break
                if isinstance(cursor, Tag) and cursor.name == 'ul':
                    run.append(cursor)
                    cursor = cursor.next_sibling
                    continue
                break
            if len(run) > 1:
                target = run[0]
                for extra in run[1:]:
                    for li in list(extra.find_all('li', recursive=False)):
                        target.append(li.extract())
                    extra.extract()
                changed += 1
                nxt = target.next_sibling
        node = nxt
    # (b) 3+ consecutive <h3> with nothing between -> <ul><li>
    node = container.contents[0] if container.contents else None
    while node is not None:
        nxt = node.next_sibling
        if isinstance(node, Tag) and node.name == 'h3':
            run = [node]
            cursor = node.next_sibling
            while cursor is not None:
                if isinstance(cursor, NavigableString):
                    if str(cursor).strip() == '':
                        cursor = cursor.next_sibling
                        continue
                    break
                if isinstance(cursor, Tag) and cursor.name == 'h3':
                    run.append(cursor)
                    cursor = cursor.next_sibling
                    continue
                break
            if len(run) >= 3:
                ul = soup.new_tag('ul')
                for item in run:
                    li = soup.new_tag('li')
                    for child in list(item.contents):
                        li.append(child.extract())
                    ul.append(li)
                    ul.append(NavigableString('\n'))
                nxt = run[-1].next_sibling
                run[0].insert_before(ul)
                for item in run:
                    item.extract()
                changed += 1
        node = nxt
    return changed
