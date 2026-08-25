# -*- coding: utf-8 -*-
"""Rule 7 (paragraph/list spacing) + flow-diagram CSS injection.
Patches the existing embedded <style> block in place -- never adds a second
stylesheet or duplicates rules that already exist."""
import re


def patch_style_block(html, accent_var, flow_css_text):
    style_m = re.search(r'(<style>)(.*?)(</style>)', html, re.DOTALL)
    if not style_m:
        return html, False
    css = style_m.group(2)
    changed = False

    # Rule 7a: bare `p{...}` (not `.foo p{...}`) gets a first-line indent.
    def add_text_indent(m):
        nonlocal changed
        body = m.group(1)
        if 'text-indent' in body:
            return m.group(0)
        changed = True
        sep = ';' if body.strip() and not body.strip().endswith(';') else ''
        return 'p{' + body + sep + 'text-indent:1.4em}'

    css2 = re.sub(r'(?:^|(?<=[};]))p\{([^}]*)\}', add_text_indent, css, count=1)

    # Rule 7b: `ul{...}` and `ol{...}` get extra left padding (~46px).
    def bump_padding(tag):
        def _sub(m):
            nonlocal changed
            body = m.group(1)
            if 'padding-left' in body:
                new_body = re.sub(r'padding-left:\s*\d+px', 'padding-left:46px', body)
            else:
                sep = ';' if body.strip() and not body.strip().endswith(';') else ''
                new_body = body + sep + 'padding-left:46px'
            if new_body != body:
                changed = True
            return tag + '{' + new_body + '}'
        return _sub

    css3 = re.sub(r'(?:^|(?<=[};]))ul\{([^}]*)\}', bump_padding('ul'), css2, count=1)
    if 'ol{' not in css3 and re.search(r'(?:^|(?<=[};]))ul\{', css3):
        # ensure <ol> (if used) gets the same left padding as <ul>
        css3 = re.sub(r'((?:^|(?<=[};]))ul\{[^}]*\})', r'\1ol{padding-left:46px;margin:0 0 10px}', css3, count=1)
        changed = True

    if '.flow{' not in css3:
        css3 = css3 + flow_css_text
        changed = True

    if not changed:
        return html, False
    new_html = html[:style_m.start(2)] + css3 + html[style_m.end(2):]
    return new_html, True
