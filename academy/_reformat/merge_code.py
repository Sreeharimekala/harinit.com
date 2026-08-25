# -*- coding: utf-8 -*-
"""Rule 1: merge shredded code blocks back into one <pre class="code-block"><code>.
Operates on the raw HTML file for "source" files (academy/AI & ML/), where lesson
content is flat siblings inside <main id="main">.
"""
import re, sys, html as htmllib
from bs4 import BeautifulSoup, NavigableString, Tag

OPENERS = '([{'
CLOSERS = ')]}'
CONTINUATION_END_RE = re.compile(r'[,+\-*/=%&|^\\]\s*$|:\s*$')


def bracket_delta(text):
    return sum(1 for c in text if c in OPENERS) - sum(1 for c in text if c in CLOSERS)


def last_nonempty_line(text):
    lines = [ln for ln in text.replace('\r\n', '\n').split('\n') if ln.strip()]
    return lines[-1].strip() if lines else ''


def is_open_after(text_so_far, running_balance):
    """True if, after accounting for text_so_far, a statement is still
    incomplete (unclosed brackets, or the last line trails an operator/':' )."""
    if running_balance > 0:
        return True
    last = last_nonempty_line(text_so_far)
    if not last:
        return False
    return bool(CONTINUATION_END_RE.search(last))


def reindent(lines):
    """Level-based (not raw-bracket-count) indentation: each line that nets
    open brackets bumps the level by exactly one step, regardless of how many
    brackets it opened; ':'-terminated lines at bracket-level 0 push a
    stacking block level so nested for/if bodies indent correctly."""
    out = []
    bracket_level = 0
    block_level = 0
    for raw in lines:
        stripped = raw.strip()
        leading_close = bool(re.match(r'^[)\]}]', stripped))
        this_bracket_level = bracket_level - (1 if leading_close else 0)
        indent = max(0, this_bracket_level + block_level) * 4
        out.append(' ' * indent + stripped)
        opens = len(re.findall(r'[([{]', stripped))
        closes = len(re.findall(r'[)\]}]', stripped))
        net = opens - closes
        if net > 0:
            bracket_level += 1
        elif net < 0:
            bracket_level = max(0, bracket_level - 1)
        if stripped.endswith(':') and bracket_level == 0:
            block_level += 1
    return '\n'.join(out)


def _is_code_pre(node):
    return isinstance(node, Tag) and node.name == 'pre' and 'code-block' in (node.get('class') or [])


def _piece_text(node):
    if node.name == 'pre':
        ct = node.find('code')
        return (ct.get_text() if ct else node.get_text())
    return node.get_text()


def merge_runs(soup, container):
    """Identity-safe: walks via .next_sibling pointers, never re-searches by
    equality (BeautifulSoup Tag equality is structural, not identity-based,
    so list.index(tag) can silently match the wrong element).

    A run only ever extends past a code block while the accumulated code is
    genuinely incomplete (unclosed brackets, or the last line trails an
    operator/':' ) -- never based on "this text looks short/code-ish", which
    is what previously swallowed real section labels into code comments.
    """
    changed = 0
    node = container.contents[0] if container.contents else None
    while node is not None:
        nxt_after_node = node.next_sibling
        if _is_code_pre(node):
            run = [node]
            text_acc = _piece_text(node)
            open_flag = is_open_after(text_acc, bracket_delta(text_acc))
            cursor = node.next_sibling
            while open_flag and cursor is not None:
                if isinstance(cursor, NavigableString):
                    if str(cursor).strip() == '':
                        cursor = cursor.next_sibling
                        continue
                    break
                if not isinstance(cursor, Tag):
                    break
                if _is_code_pre(cursor) or cursor.name == 'p':
                    piece_text = _piece_text(cursor)
                    stripped = piece_text.strip()
                    if not stripped or len(stripped) > 200 or stripped.endswith(('.', '?', '!')):
                        break
                    run.append(cursor)
                    text_acc = text_acc + '\n' + piece_text
                    open_flag = is_open_after(text_acc, bracket_delta(text_acc))
                    cursor = cursor.next_sibling
                    continue
                break
            if len(run) > 1:
                lines = []
                for piece in run:
                    text = _piece_text(piece).replace('\r\n', '\n').replace('\r', '\n')
                    lines.extend(ln.rstrip() for ln in text.split('\n') if ln.strip() != '')
                merged_text = reindent(lines)
                new_pre = soup.new_tag('pre')
                new_pre['class'] = 'code-block'
                new_code = soup.new_tag('code')
                new_code.string = merged_text
                new_pre.append(new_code)
                nxt_after_node = run[-1].next_sibling
                run[0].insert_before(new_pre)
                for piece in run:
                    piece.extract()
                changed += 1
        node = nxt_after_node
    return changed
