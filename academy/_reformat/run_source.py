# -*- coding: utf-8 -*-
import re, sys, os
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge_code import merge_runs
from structure_rules import (
    rule5_flow_diagrams, rule3_labels_and_numbered, rule2_listify,
    rule4_bold_questions, rule6_h3_runs_and_adjacent_uls, flow_css,
)
from css_patch import patch_style_block

SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AI & ML")

FILES = [
    "Module_1_Python_Programming.html",
    "Module_2_SQL_for_Data_Science.html",
    "Module_3_Mathematics_for_AI.html",
    "Module_4_Data_Structures_and_Algorithms.html",
    "Module_5_Statistics.html",
    "Module_6_Data_Analysis_and_Visualization.html",
    "module_7_machine_learning.html",
    "Module_8_Deep_Learning.html",
    "Module_9_Natural_Language_Processing.html",
    "Module_10_MLOps_and_Cloud.html",
    "Module_11_Generative_AI_and_LLMs.html",
    "Module_12_Capstone_Projects.html",
]


def word_count(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    return len(re.findall(r'\S+', soup.get_text(separator=' ')))


def alnum_tokens(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    return re.findall(r'[A-Za-z0-9_]+', soup.get_text(separator=' '))


def process_file(path, write=False):
    html = open(path, encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    if main is None:
        return None
    counts = {}
    counts['merge_code'] = merge_runs(soup, main)
    counts['flow_diagrams'] = rule5_flow_diagrams(soup, main)
    counts['labels_headings'] = rule3_labels_and_numbered(soup, main)
    counts['listify'] = rule2_listify(soup, main)
    counts['bold_questions'] = rule4_bold_questions(soup, main)
    counts['h3run_adjacentul'] = rule6_h3_runs_and_adjacent_uls(soup, main)
    out = str(soup)
    out2, css_changed = patch_style_block(out, '--teal', flow_css('--teal'))
    counts['css_patched'] = css_changed
    before_wc, after_wc = word_count(html), word_count(out2)
    before_tok, after_tok = alnum_tokens(html), alnum_tokens(out2)
    token_match = before_tok == after_tok
    if write and token_match:
        open(path, 'w', encoding='utf-8').write(out2)
    return {
        'file': os.path.basename(path), 'counts': counts,
        'before_words': before_wc, 'after_words': after_wc,
        'token_match': token_match,
        'before_tokens': len(before_tok), 'after_tokens': len(after_tok),
    }


if __name__ == '__main__':
    write = '--write' in sys.argv
    results = []
    for fname in FILES:
        path = os.path.join(SRC_DIR, fname)
        r = process_file(path, write=write)
        results.append(r)
        status = 'OK' if r['token_match'] else 'MISMATCH!!'
        print(f"{r['file']:<45} words {r['before_words']:>6} -> {r['after_words']:>6}  "
              f"alnum-tokens {r['before_tokens']:>6} -> {r['after_tokens']:>6}  [{status}]  "
              f"code={r['counts']['merge_code']:>3} flow={r['counts']['flow_diagrams']:>3} "
              f"h3/h4={r['counts']['labels_headings']:>3} lists={r['counts']['listify']:>3} "
              f"bold?={r['counts']['bold_questions']:>3} cleanup={r['counts']['h3run_adjacentul']:>2} "
              f"css={'patched' if r['counts']['css_patched'] else 'unchanged'}")
    n_bad = sum(1 for r in results if not r['token_match'])
    print()
    print('ALL FILES TOKEN-SAFE' if n_bad == 0 else f'{n_bad} FILE(S) HAVE TOKEN MISMATCHES -- NOT WRITTEN')
