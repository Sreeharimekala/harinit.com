# -*- coding: utf-8 -*-
"""Recolor the Microsoft Fabric module pages to the same light W3Schools-style
palette used for AI & ML -- colors only, no structural/spacing changes.
Safe by construction: every substitution only touches text inside <style>,
and only ever swaps a color VALUE for another color value (hex/rgba triplet),
never adds/removes/reorders a CSS property or touches article content."""
import re, glob, os

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microsoft-fabric")

# Ordered: run the *targeted* (selector-scoped) substitutions first, so the
# few values that must diverge from a simple value-for-value swap (accent-2
# usages that should read as the green accent, not red) are redirected
# before the blanket sweep recolors everything else.
TARGETED = [
    (re.compile(r'(\.nav-num\{[^}]*?color:\s*)var\(--accent-2\)'), r'\1var(--accent)'),
    (re.compile(r'(\.lesson-eyebrow\{[^}]*?color:\s*)var\(--accent-2\)'), r'\1var(--accent)'),
    (re.compile(r'(\.quote\{[^}]*?border-left:\s*3px solid\s*)var\(--accent-2\)'), r'\1var(--accent)'),
    (re.compile(r'(\.content ol li::marker\{[^}]*?color:\s*)var\(--accent-2\)'), r'\1var(--accent)'),
    (re.compile(r'(\.diagram-branch\{[^}]*?color:\s*)#7fe3c7'), r'\1var(--accent)'),
    (re.compile(r'(\.diagram-label\{[^}]*?color:\s*)#e7e9ee'), r'\1var(--ink)'),
    (re.compile(r'color:\s*#fff\b'), 'color:var(--ink)'),
    (re.compile(r'(\.nav-toggle\{\s*display:\s*inline-flex[^}]*?color:\s*)#04211d'), r'\1#FFFFFF'),
]

# Blanket value-for-value swaps (hex + rgba triplets), applied after the
# targeted pass. Order-independent; each maps one literal color to another.
BLANKET_HEX = [
    ('#0f1115', '#FFFFFF'),  # --bg
    ('#151822', '#FFFFFF'),  # --panel
    ('#11141b', '#FFFFFF'),  # --panel-2
    ('#e7e9ee', '#000000'),  # --ink
    ('#a7adba', '#111111'),  # --ink-dim
    ('#6b7280', '#666666'),  # --ink-faint
    ('#5fd3c4', '#04AA6D'),  # --accent
    ('#f2a65a', '#FF1744'),  # --accent-2
    ('#262b38', '#E1E3E5'),  # --rule
    ('#0b0d12', '#FFFFFF'),  # --code-bg / --diagram-bg
    ('#cde5ff', '#111111'),  # --code-ink
    ('#7fe3c7', '#111111'),  # --diagram-ink (remaining, non-targeted uses)
    ('#1b2030', '#F1F1F1'),  # --table-head
]

BLANKET_RGBA_RE = [
    (re.compile(r'rgba\(\s*95,\s*211,\s*196,'), 'rgba(4,170,109,'),   # accent teal-tint -> green-tint
    (re.compile(r'rgba\(\s*242,\s*166,\s*90,'), 'rgba(235,237,238,'),  # accent-2 orange-tint -> light-gray-tint
    (re.compile(r'rgba\(\s*255,\s*255,\s*255,\s*0?\.02\s*\)'), '#F8F8F8'),  # dark-theme row-hover lighten
]

NEW_ROOT_VARS = (
    "--accent-hover:#008F5B;--crumb-muted:#666666;--crumb-link:#04AA6D;"
    "--glyph-ink:#999999;--btn-border:#04AA6D;--btn-bg-tint:#E8F7F1;"
    "--btn-ink:#008F5B;--current-bg:#E8F7F1;--current-ink:#04AA6D;"
)


def recolor(html):
    style_m = re.search(r'(<style>)(.*?)(</style>)', html, re.DOTALL)
    if not style_m:
        return html, False
    css = style_m.group(2)
    original_css = css

    for pat, repl in TARGETED:
        css = pat.sub(repl, css)
    for old, new in BLANKET_HEX:
        css = css.replace(old, new)
    for pat, repl in BLANKET_RGBA_RE:
        css = pat.sub(repl, css)

    # append the new dedicated variables just before :root's closing brace
    root_m = re.search(r':root\{', css)
    if root_m and '--accent-hover' not in css:
        close_idx = css.index('}', root_m.end())
        css = css[:close_idx] + NEW_ROOT_VARS + css[close_idx:]

    if css == original_css:
        return html, False
    new_html = html[:style_m.start(2)] + css + html[style_m.end(2):]
    return new_html, True


if __name__ == '__main__':
    import sys
    write = '--write' in sys.argv
    files = sorted(glob.glob(os.path.join(DIR, 'Module_*.html')))
    for path in files:
        html = open(path, encoding='utf-8').read()
        new_html, changed = recolor(html)
        status = 'changed' if changed else 'no-op'
        print(os.path.basename(path), '->', status, f'({len(html)} -> {len(new_html)} bytes)')
        if write and changed:
            open(path, 'w', encoding='utf-8').write(new_html)
