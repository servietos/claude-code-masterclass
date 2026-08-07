"""Programmatic overflow detector.

Walks every slide, estimates rendered text height per text-frame, and
flags any frame where the estimated content height exceeds the box.
Also flags shapes that extend beyond slide bounds.
"""

import os
import re
import sys
import zipfile
from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

# OOXML coordinate attributes are ST_Coordinate / ST_PositiveCoordinate —
# integers only. A float leaks in whenever a renderer passes an unrounded
# EMU expression to python-pptx, and PowerPoint then refuses to open the
# file with "PowerPoint could not open the file".
_NUMERIC_ATTR = re.compile(
    r'\b(?:x|y|cx|cy|w|h|sz|rot|pos|ang|off|marL|marR|marT|marB)="([^"]*)"')


def check_integer_coordinates(pptx_path):
    """Fail loudly on non-integer coordinate attributes anywhere in the deck."""
    findings = []
    with zipfile.ZipFile(pptx_path) as z:
        for name in z.namelist():
            if not name.endswith('.xml'):
                continue
            xml = z.read(name).decode('utf-8', 'replace')
            for m in _NUMERIC_ATTR.finditer(xml):
                if '.' in m.group(1):
                    findings.append((name, m.group(0)))
    return findings


def emu_to_in(v):
    return float(v) / 914400.0


def pt_to_in(pt):
    return float(pt) / 72.0


def estimate_text_height_in(tf, frame_w_in, frame_h_in):
    """Estimate rendered text height for a text frame, in inches.

    Counts lines (approx by wrap), uses font size * line_spacing factor.
    """
    total_pt = 0
    for p in tf.paragraphs:
        # line spacing — default 1.0, but our boxes set explicit values
        ls = 1.15
        lnSpc = p._pPr.find(qn('a:lnSpc')) if p._pPr is not None else None
        if lnSpc is not None:
            spcPct = lnSpc.find(qn('a:spcPct'))
            if spcPct is not None:
                val = spcPct.get('val')
                if val:
                    ls = int(val) / 100000.0

        max_run_pt = 12
        line_text = ''
        for r in p.runs:
            sz_pt = (r.font.size.pt if r.font.size else 12)
            max_run_pt = max(max_run_pt, sz_pt)
            line_text += r.text or ''
        # Approximate chars per line based on width (~0.55 * font_pt per char in pixels — rough)
        # Use 0.55 * pt to in: pt * 0.55 / 72
        if line_text:
            char_w_in = max_run_pt * 0.55 / 72.0
            chars_per_line = max(1, int(frame_w_in / max(char_w_in, 0.05)))
            n_lines = max(1, (len(line_text) + chars_per_line - 1) // chars_per_line)
        else:
            n_lines = 1
        line_h_pt = max_run_pt * ls
        total_pt += line_h_pt * n_lines

    # add inset margins ~0.06" top+bottom
    return pt_to_in(total_pt) + 0.08


def shape_label(shp):
    if shp.has_text_frame:
        t = shp.text_frame.text.strip().replace('\n', ' / ')
        return t[:80]
    return '<shape>'


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: validate.py <deck.pptx>')
    pptx_path = sys.argv[1]

    coord_findings = check_integer_coordinates(pptx_path)
    for name, attr in coord_findings[:20]:
        print(f'  [NON-INTEGER-COORD] {name} {attr}')
    print(f'Non-integer coordinates: {len(coord_findings)}')

    prs = Presentation(pptx_path)
    slide_w_in = emu_to_in(prs.slide_width)
    slide_h_in = emu_to_in(prs.slide_height)

    issues = []

    # known false-positive labels — watermarks, page numbers, time slots
    IGNORE_LABELS = {
        "Fast Lane · Claude Code Masterclass",
    }

    for i, slide in enumerate(prs.slides, start=1):
        for shp in slide.shapes:
            try:
                if shp.left is None or shp.top is None:
                    continue
                x = emu_to_in(shp.left)
                y = emu_to_in(shp.top)
                w = emu_to_in(shp.width)
                h = emu_to_in(shp.height)
            except Exception:
                continue

            # Shape extends beyond slide
            if x + w > slide_w_in + 0.02:
                issues.append((i, 'OOB-right', shape_label(shp),
                               f'{x+w:.2f}"/{slide_w_in:.2f}"'))
            if y + h > slide_h_in + 0.02:
                issues.append((i, 'OOB-bottom', shape_label(shp),
                               f'{y+h:.2f}"/{slide_h_in:.2f}"'))

            # Filled card overlapping the footer/watermark band. Excludes
            # full-bleed backgrounds, full-height edge bars, and the bottom
            # accent strip — only content cards are flagged.
            safe_bottom = slide_h_in - 0.55
            is_filled_card = False
            try:
                is_filled_card = (shp.shape_type == 1 and
                                  shp.fill.type == 1)
            except Exception:
                is_filled_card = False
            full_width = w > slide_w_in * 0.97
            bottom_strip = y > slide_h_in - 0.25
            if (is_filled_card and y > 0.1 and h < slide_h_in * 0.9
                    and not full_width and not bottom_strip
                    and y + h > safe_bottom + 0.02):
                issues.append((i, 'FOOTER-overlap', shape_label(shp),
                               f'bottom {y+h:.2f}" > safe {safe_bottom:.2f}"'))

            if not shp.has_text_frame:
                continue

            tf = shp.text_frame
            if not tf.text.strip():
                continue
            label = tf.text.strip()
            if label in IGNORE_LABELS:
                continue
            # page numbers like "X / 234"
            if '/' in label and len(label) < 12:
                continue

            est_h = estimate_text_height_in(tf, max(w - 0.1, 0.1), h)
            # require >20% overflow to flag (small box widgets have padding)
            if est_h > h + 0.15 and est_h > h * 1.15:
                issues.append((i, 'TEXT-overflow',
                               shape_label(shp),
                               f'est {est_h:.2f}" > box {h:.2f}"'))

    # Group + report
    by_slide = {}
    for s, kind, lbl, info in issues:
        by_slide.setdefault(s, []).append((kind, lbl, info))

    print(f'Slides scanned: {len(prs.slides)}')
    print(f'Slides with potential overflow: {len(by_slide)}')
    print(f'Total findings: {len(issues) + len(coord_findings)}')
    print()
    # show top offenders
    for s in sorted(by_slide.keys()):
        lst = by_slide[s]
        print(f'=== Slide {s} ({len(lst)} issues) ===')
        for kind, lbl, info in lst[:8]:
            print(f'  [{kind}] "{lbl[:50]}" {info}')


if __name__ == '__main__':
    main()
