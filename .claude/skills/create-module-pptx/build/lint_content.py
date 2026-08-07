"""Lint a module content YAML against what the renderers actually consume.

The renderers ignore any field they do not know, so a typo or a field placed on
the wrong slide type disappears silently at build time. This catches that before
the deck is built, plus the length limits that cause text to overflow its box.

    python lint_content.py demos/01-fundamentals/pptx/module-01.yaml
"""

import sys
import yaml

sys.stdout.reconfigure(encoding='utf-8')

# Injected by build_pptx.py on every slide, legal everywhere.
COMMON = {'type', 'notes', 'module', 'day', 'time',
          'chapter', 'chapter_total', 'chapter_label'}

FIELDS = {
    'divider': {'module_number', 'title', 'subtitle', 'time', 'icon'},
    'objectives': {'title', 'subtitle', 'items'},
    'lab': {'title', 'duration', 'steps', 'outcome'},
    'takeaways': {'title', 'subtitle', 'items'},
    'bullets': {'title', 'subtitle', 'items'},
    'content': {'title', 'subtitle', 'columns'},
    'table': {'title', 'subtitle', 'headers', 'rows'},
    'code': {'title', 'subtitle', 'language', 'code', 'caption', 'side'},
    'terminal': {'title', 'subtitle', 'window', 'lines', 'caption', 'side'},
    'callout': {'title', 'subtitle', 'text'},
    'statement': {'kicker', 'text', 'attribution'},
    'quote': {'text', 'author'},
    'discussion': {'title', 'prompt'},
    'diagram': {'title', 'subtitle', 'diagram_type', 'caption', 'left', 'right',
                'rows', 'nodes', 'steps', 'actors', 'messages', 'cards',
                'quadrants', 'x_axis', 'y_axis', 'highlight_index', 'd2', 'chart'},
}

# Only these render a caption. Everything else discards it.
CAPTION_OK = {'code', 'terminal'}
CAPTION_OK_DIAGRAM = {'flow', 'architecture'}

MAX = {'title': 45, 'subtitle': 60, 'item': 60, 'cell': 55,
       'side_heading': 30, 'side_item': 44}


def lint(path):
    doc = yaml.safe_load(open(path, encoding='utf-8'))
    out = []

    def bad(i, msg):
        out.append(f'  slide {i:2d}: {msg}')

    slides = doc.get('slides') or []
    for i, s in enumerate(slides, start=1):
        t = s.get('type')
        if t not in FIELDS:
            bad(i, f'unknown slide type {t!r}')
            continue

        for k in set(s) - FIELDS[t] - COMMON:
            bad(i, f'[{t}] field {k!r} is not read by the renderer, content is lost')

        if 'notes' not in s and t != 'divider':
            bad(i, f'[{t}] no presenter notes')

        if 'caption' in s:
            dt = s.get('diagram_type')
            ok = t in CAPTION_OK or (t == 'diagram' and dt in CAPTION_OK_DIAGRAM)
            if not ok:
                where = f'{t}/{dt}' if t == 'diagram' else t
                bad(i, f'[{where}] caption is DISCARDED by this renderer, move it '
                       f'to subtitle: {s["caption"][:50]!r}')

        for f in ('title', 'subtitle'):
            v = s.get(f)
            if isinstance(v, str) and len(v) > MAX[f]:
                bad(i, f'[{t}] {f} is {len(v)} chars (max {MAX[f]}): {v[:55]!r}')

        for f in ('items', 'steps'):
            for v in s.get(f) or []:
                if isinstance(v, str) and len(v) > MAX['item']:
                    bad(i, f'[{t}] {f} entry is {len(v)} chars (max {MAX["item"]}): {v[:55]!r}')
        if len(s.get('items') or []) > 6:
            bad(i, f'[{t}] {len(s["items"])} items (max 6)')

        if t == 'statement' and 'title' in s:
            bad(i, 'statement has no title field, use kicker')

        if t == 'table':
            heads = s.get('headers') or []
            if len(heads) != 2:
                bad(i, f'table has {len(heads)} headers (must be exactly 2)')
            rows = s.get('rows') or []
            if len(rows) > 5:
                bad(i, f'table has {len(rows)} rows (max 5)')
            for r in rows:
                if len(r) != len(heads):
                    bad(i, f'table row has {len(r)} cells, headers have {len(heads)}')
                for c in r:
                    if len(str(c)) > MAX['cell']:
                        bad(i, f'table cell is {len(str(c))} chars (max {MAX["cell"]}): {str(c)[:50]!r}')

        side = s.get('side')
        if side is not None:
            if not isinstance(side, dict):
                bad(i, f'[{t}] side must be a mapping of heading and items')
            else:
                for k in set(side) - {'heading', 'items'}:
                    bad(i, f'[{t}] side field {k!r} is not read by the renderer')
                if not side.get('heading'):
                    bad(i, f'[{t}] side has no heading')
                elif len(side['heading']) > MAX['side_heading']:
                    bad(i, f'[{t}] side heading is {len(side["heading"])} chars '
                           f'(max {MAX["side_heading"]})')
                si = side.get('items') or []
                if len(si) > 5:
                    bad(i, f'[{t}] side has {len(si)} items (max 5)')
                for v in si:
                    if len(v) > MAX['side_item']:
                        bad(i, f'[{t}] side item is {len(v)} chars '
                               f'(max {MAX["side_item"]}): {v[:50]!r}')

        if t == 'terminal':
            lines = s.get('lines') or []
            if len(lines) > 9:
                bad(i, f'terminal has {len(lines)} lines (max 9)')
            for l in lines:
                if l.get('t') not in ('comment', 'cmd', 'out', 'ok', 'err'):
                    bad(i, f'terminal line kind {l.get("t")!r} is unknown')
                # A rail narrows the window; past this the whole block is
                # rendered a size down to keep fitting.
                if side and len(l.get('text', '')) > 50:
                    bad(i, f'terminal line is {len(l["text"])} chars (max 50 '
                           f'beside a side rail): {l["text"][:45]!r}')

        if t == 'code' and side:
            for cl in (s.get('code') or '').split('\n'):
                if len(cl) > 56:
                    bad(i, f'code line is {len(cl)} chars (max 56 beside a '
                           f'side rail): {cl[:45]!r}')

        if t == 'diagram':
            dt = s.get('diagram_type')
            if dt == 'comparison':
                l, r = s.get('left') or {}, s.get('right') or {}
                if ('variant' in l) != ('variant' in r):
                    bad(i, 'comparison sets variant on ONE side only, the other '
                           'silently renders red. Set both or neither.')
                for side, d in (('left', l), ('right', r)):
                    for v in d.get('items') or []:
                        if len(v) > MAX['item']:
                            bad(i, f'{side} item is {len(v)} chars (max {MAX["item"]}): {v[:55]!r}')
            elif dt == 'architecture':
                rows = s.get('rows')
                if not isinstance(rows, list) or not all(isinstance(r, list) for r in rows or []):
                    bad(i, 'architecture rows must be a LIST OF LISTS')
            elif dt == 'decision':
                if len(s.get('nodes') or []) > 4:
                    bad(i, f'decision has {len(s["nodes"])} nodes (max 4)')
            elif dt == 'flow':
                steps = s.get('steps') or []
                if len(steps) > 5:
                    bad(i, f'flow has {len(steps)} steps (max 5)')
                # A flow step box is short and narrow; label and desc share it.
                for st in steps:
                    lab, desc = st.get('label', ''), st.get('desc', '')
                    if len(lab) > 22:
                        bad(i, f'flow step label is {len(lab)} chars (max 22): {lab!r}')
                    if len(lab) + len(desc) > 56:
                        bad(i, f'flow step label+desc is {len(lab) + len(desc)} chars '
                               f'(max 56), it will overflow the box: {lab!r}')

    for i, s in enumerate(slides, start=1):
        for k, v in s.items():
            if isinstance(v, str) and '—' in v:
                bad(i, f'em dash in {k!r}')

    types = {}
    for s in slides:
        key = s.get('diagram_type') if s.get('type') == 'diagram' else s.get('type')
        types[key] = types.get(key, 0) + 1

    print(f'{path}: {len(slides)} slides')
    print('  mix: ' + ', '.join(f'{k} x{v}' for k, v in sorted(types.items(), key=lambda kv: -kv[1])))
    if out:
        print('\n'.join(out))
    print(f'  findings: {len(out)}')
    return len(out)


if __name__ == '__main__':
    total = sum(lint(p) for p in sys.argv[1:])
    sys.exit(1 if total else 0)
