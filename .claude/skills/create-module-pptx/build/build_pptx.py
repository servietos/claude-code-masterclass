"""Build one module deck from a module YAML file.

This is the skill-local copy of the course generator. It builds exactly one
module at a time.
"""

import argparse
import os
import sys
import yaml

sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation

import theme
from helpers import add_watermark
from layouts import (
    render_title_hero, render_day_hero, render_divider, render_objectives,
    render_content, render_bullets, render_diagram, render_code,
    render_table, render_callout, render_lab, render_discussion,
    render_takeaways, render_chapter_opener, render_chapter_contents,
    render_closing_cta, render_chart, render_terminal, render_statement,
    render_quote,
)


RENDERERS = {
    'title_hero': render_title_hero,
    'day_hero': render_day_hero,
    'chapter_opener': render_chapter_opener,
    'chapter_contents': render_chapter_contents,
    'closing_cta': render_closing_cta,
    'divider': render_divider,
    'objectives': render_objectives,
    'content': render_content,
    'bullets': render_bullets,
    'diagram': render_diagram,
    'chart': render_chart,
    'terminal': render_terminal,
    'statement': render_statement,
    'quote': render_quote,
    'code': render_code,
    'table': render_table,
    'callout': render_callout,
    'lab': render_lab,
    'discussion': render_discussion,
    'takeaways': render_takeaways,
}


# slide types that should not show the corner watermark/page-num
HERO_TYPES = {'title_hero', 'day_hero', 'chapter_opener', 'closing_cta'}


# 5 chapters grouping the 14 modules. The chapter opener (art + two-tone
# headline) replaces the old Day 1 / Day 2 heroes.
CHAPTERS = [
    {'num': 1, 'title': 'Foundations', 'accent': 'How Claude Code thinks',
     'subtitle': 'Fundamentals, then configuring the harness for the way you work.',
     'modules': [1, 2]},
    {'num': 2, 'title': 'Extending the Agent', 'accent': 'Tools & Skills',
     'subtitle': 'Give Claude new capabilities with MCP tools and Skills.',
     'modules': [3, 4]},
    {'num': 3, 'title': 'Engineering Speed', 'accent': 'Plan · parallelize · coordinate',
     'subtitle': 'Spec-driven work, focused sub-agents, and teams that talk to each other.',
     'modules': [5, 6, 7, 8]},
    {'num': 4, 'title': 'Automation', 'accent': 'Headless & managed',
     'subtitle': 'Run Claude Code without a human in the loop.',
     'modules': [9, 10]},
    {'num': 5, 'title': 'Ship & Operate', 'accent': 'Secure · distribute · deploy',
     'subtitle': 'Hardening, plugins, the SDK, and agentic DevOps.',
     'modules': [11, 12, 13, 14]},
]

_CH_OF_MODULE = {m: c for c in CHAPTERS for m in c['modules']}


def _chapter_opener_slide(c):
    return {'type': 'chapter_opener', 'chapter': c['num'],
            'label': f"Chapter {c['num']} · {c['title']}",
            'title': c['title'], 'accent_line': c['accent'],
            'subtitle': c['subtitle']}


def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def render_deck(slide_dicts, out_path):
    """Render a list of slide dicts into one .pptx with per-deck page numbers."""
    prs = Presentation()
    prs.slide_width = theme.SLIDE_W
    prs.slide_height = theme.SLIDE_H
    total = len(slide_dicts)
    page_num = 0
    for slide_data in slide_dicts:
        page_num += 1
        slide_type = slide_data.get('type', 'bullets')
        renderer = RENDERERS.get(slide_type)
        if renderer is None:
            print(f"  ! unknown slide type '{slide_type}' on slide {page_num}")
            continue
        try:
            slide_obj = renderer(prs, slide_data)
        except Exception as e:
            print(f"  ! error on slide {page_num} ({slide_type}): {e}")
            raise
        if slide_type not in HERO_TYPES:
            add_watermark(slide_obj, page_num=page_num, total=total)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    prs.save(out_path)
    return total


def _module_slides(data, *, with_opener):
    """Slides for one module file — optional chapter opener + its own slides,
    with day_hero filtered out and chapter/module metadata propagated."""
    mod_day = data.get('day')
    mod_num = data.get('module')
    chap = _CH_OF_MODULE.get(mod_num)
    # The chapter map is keyed by the combined deck's module numbering, which
    # demos/ does not follow, so a file header naming a chapter wins over it.
    ch_num = data.get('chapter', chap['num'] if chap else None)
    ch_total = data.get('chapter_total', len(CHAPTERS))
    ch_label = data.get('chapter_label', chap['title'] if chap else '')
    out = []
    if with_opener and chap:
        out.append(_chapter_opener_slide(chap))
    for s in data.get('slides', []):
        if s.get('type') == 'day_hero':
            continue
        if mod_day is not None and 'day' not in s:
            s['day'] = mod_day
        if mod_num is not None and 'module' not in s:
            s['module'] = mod_num
        if ch_num:
            s.setdefault('chapter', ch_num)
            s.setdefault('chapter_total', ch_total)
            s.setdefault('chapter_label', ch_label)
        out.append(s)
    return out


def build_one(content_path, out_path, with_opener=True):
    """Render a single module YAML into a standalone deck at out_path."""
    data = load_yaml(content_path)
    n = render_deck(_module_slides(data, with_opener=with_opener), out_path)
    print(f"{os.path.basename(out_path)} — {n} slides -> {out_path}")
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content', required=True,
                        help='the module YAML file to build')
    parser.add_argument('--out', required=True, help='output .pptx path')
    parser.add_argument('--no-opener', action='store_true',
                        help='omit the chapter opener slide')
    args = parser.parse_args()

    build_one(args.content, args.out, with_opener=not args.no_opener)


if __name__ == '__main__':
    main()
