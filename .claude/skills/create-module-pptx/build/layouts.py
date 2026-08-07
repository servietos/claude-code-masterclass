"""Per-slide layout renderers."""

import os
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from theme import (
    DARK, DARKER, CORAL, AMBER, GOLD, LIGHT, MUTED, WHITE, NAVY_GRAD,
    PANEL_BG, CODE_BG, GREEN, RED, BAD_BG, GOOD_BG,
    CARD, CARD_HI, PANEL_HI, PRIMARY, ACCENT, POP, PRIMARY_BRIGHT,
    GROUND, GROUND2, TEXT, TEXT_MUTED, ON_PRIMARY,
    FONT_HEADING, FONT_BODY, FONT_MONO,
    SLIDE_W, SLIDE_H, MARGIN_X, MARGIN_TOP, CONTENT_W,
    TITLE_TOP, TITLE_H, BODY_TOP, BODY_H, CONTENT_SAFE_BOTTOM,
    SZ_HERO_TITLE, SZ_HERO_SUBTITLE, SZ_HERO_TAGLINE,
    SZ_TITLE, SZ_SUBTITLE, SZ_H3, SZ_BODY, SZ_SMALL, SZ_TINY, SZ_CODE,
)
from helpers import (
    add_rect, add_text, add_multi_text, add_arrow,
    set_solid_fill, set_line, set_slide_background,
    set_slide_background_gradient, add_title, add_watermark,
)
from diagrams import (
    render_flow, render_architecture, render_sequence,
    render_comparison, render_metrics, render_decision, render_quadrant,
)
from design import (
    accent_for, add_header, add_bg_accent, content_band, window_chrome,
    add_bar_chart, add_donut_chart, add_progress_rows, optical_top,
)
from pptx.util import Emu


IMAGES_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..', 'images'))
ICONS_DIR = os.path.join(IMAGES_DIR, 'icons')


def _icon_path(name):
    """Resolve an icon name to a PNG path, or None if missing."""
    if not name:
        return None
    p = os.path.join(ICONS_DIR, f'{name}.png')
    return p if os.path.exists(p) else None


def _add_icon(slide, name, x, y, w, h):
    p = _icon_path(name)
    if not p:
        return None
    return slide.shapes.add_picture(p, int(x), int(y), int(w), int(h))


def _add_blank_slide(prs):
    blank_layout = prs.slide_layouts[6]
    return prs.slides.add_slide(blank_layout)


SIDE_GAP = Inches(0.4)
SIDE_RATIO = 0.63


def split_band():
    """Left panel width, right rail x, right rail width for a two-column slide."""
    left_w = int((CONTENT_W - SIDE_GAP) * SIDE_RATIO)
    right_w = int(CONTENT_W - SIDE_GAP - left_w)
    return left_w, int(MARGIN_X + left_w + SIDE_GAP), right_w


def fit_block(texts, box_w_in, box_h_in, sizes, line_spacing,
              char_ratio=0.62, slack=1.05):
    """Largest size from `sizes` at which the wrapped block fits the box.

    Returns (point_size, estimated_height_in). Wrapping is counted, and the
    line box is taken as 1.2x the point size (what PowerPoint applies the
    percentage spacing to) plus a slack factor, so a substituted font that
    runs taller than the design font still lands inside the frame.
    """
    chosen, height = sizes[-1], 0.0
    for pt in sizes:
        char_w = pt * char_ratio / 72.0
        per_line = max(8, int(box_w_in / char_w))
        n = sum(max(1, -(-len(t) // per_line)) for t in texts) or 1
        chosen = pt
        height = n * pt * 1.2 * line_spacing / 72.0 * slack
        if height <= box_h_in:
            break
    return chosen, height


RAIL_HEAD_H = Inches(0.62)
RAIL_PAD = Inches(0.42)


def measure_side_rail(side, w):
    """Height the rail needs for its own bullets, in EMU.

    The panel beside it is sized to its code or CLI lines, which is often
    shorter than the rail, so the caller takes the taller of the two.
    """
    items = (side.get('items') or [])[:6]
    text_w_in = (w - Inches(0.56)) / 914400.0
    _, h_in = fit_block([it + '  ' for it in items], text_w_in, 99.0,
                        (14,), 1.35, char_ratio=0.58)
    return int(RAIL_HEAD_H + Inches(h_in) + RAIL_PAD)


def render_side_rail(slide, x, y, w, h, side, accent):
    """Right-hand companion card: heading band plus short bullets.

    Fills the space a content-sized terminal or code panel leaves empty, and
    carries the point of the panel instead of repeating its lines.
    """
    add_rect(slide, x, y, w, h, fill=CARD, line=None, corner=0.035)
    head_h = RAIL_HEAD_H
    add_rect(slide, x, y, w, head_h, fill=accent, line=None, rounded=False)
    add_text(slide, x + Inches(0.28), y, w - Inches(0.5), head_h,
             side.get('heading', ''), size=Pt(17), color=ON_PRIMARY,
             bold=True, font=FONT_HEADING, anchor=MSO_ANCHOR.MIDDLE)
    items = (side.get('items') or [])[:6]
    lines = [{'text': it, 'bullet': '▸', 'bullet_color': accent,
              'size': Pt(14), 'color': LIGHT} for it in items]
    add_multi_text(slide, x + Inches(0.28), y + head_h + Inches(0.22),
                   w - Inches(0.56), h - head_h - Inches(0.42),
                   lines, default_size=Pt(14), line_spacing=1.35,
                   shrink_to_fit=True)


def _brandmark(slide, x, y, w, h, size=Pt(22)):
    """Fast Lane logo if the asset is present, else the styled wordmark.
    Drop a white/mono transparent PNG at images/fastlane-logo-white.png."""
    logo = os.path.join(IMAGES_DIR, 'fastlane-logo-white.png')
    if os.path.exists(logo):
        from PIL import Image as _Im
        iw, ih = _Im.open(logo).size
        dw = int(h * iw / ih)
        slide.shapes.add_picture(logo, int(x + w - dw), int(y), dw, int(h))
    else:
        add_text(slide, x, y, w, h, "Fast Lane", size=size, color=ACCENT,
                 bold=True, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)


def _embed_diagram(slide, png_path):
    """Place a generated diagram PNG in the body area, fit + centered."""
    from PIL import Image as _Im
    iw, ih = _Im.open(png_path).size
    top = BODY_TOP + Inches(0.3)
    scale = min(CONTENT_W / iw, Inches(5.0) / ih)
    w, h = int(iw * scale), int(ih * scale)
    slide.shapes.add_picture(png_path, int(MARGIN_X + (CONTENT_W - w) / 2),
                             int(top), w, h)


def render_title_hero(prs, data):
    slide = _add_blank_slide(prs)
    bg = os.path.join(IMAGES_DIR, 'title_bg.png')
    if os.path.exists(bg):
        slide.shapes.add_picture(bg, 0, 0, width=SLIDE_W, height=SLIDE_H)
    else:
        set_slide_background_gradient(slide, DARK, NAVY_GRAD)

    title = data.get('title', '')
    subtitle = data.get('subtitle', '')
    tagline = data.get('tagline', '')

    add_text(slide, MARGIN_X, Inches(0.5), CONTENT_W, Inches(0.35),
             "FAST LANE · CLAUDE CODE MASTERCLASS", size=Pt(11),
             color=MUTED, bold=True, font=FONT_BODY)
    add_rect(slide, MARGIN_X, Inches(2.55), Inches(0.9), Inches(0.045),
             fill=PRIMARY, line=None, rounded=False)
    long_title = len(title) > 22
    title_size = Pt(54) if long_title else Pt(60)
    add_text(slide, MARGIN_X, Inches(2.7), Inches(11.0), Inches(2.0),
             title, size=title_size, color=WHITE, bold=True,
             font=FONT_HEADING, line_spacing=1.02)
    if subtitle:
        add_text(slide, MARGIN_X, Inches(4.75), CONTENT_W, Inches(0.6),
                 subtitle, size=Pt(24), color=PRIMARY, font=FONT_BODY)
    if tagline:
        add_text(slide, MARGIN_X, Inches(5.45), CONTENT_W, Inches(0.5),
                 tagline, size=Pt(15), color=MUTED, italic=True, font=FONT_BODY)
    _brandmark(slide, SLIDE_W - Inches(3.0), SLIDE_H - Inches(1.0),
               Inches(2.1), Inches(0.55), size=Pt(26))
    _maybe_speaker_notes(slide, data)
    return slide


def render_day_hero(prs, data):
    slide = _add_blank_slide(prs)
    bg_name = data.get('background')
    bg_path = os.path.join(IMAGES_DIR, bg_name) if bg_name else None
    if bg_path and os.path.exists(bg_path):
        slide.shapes.add_picture(bg_path, 0, 0,
                                 width=SLIDE_W, height=SLIDE_H)
        # dark gradient overlay on bottom half
        grad_box = add_rect(slide, 0, SLIDE_H * 0.40,
                            SLIDE_W, SLIDE_H * 0.60,
                            fill=DARK, line=None, rounded=False)
    else:
        set_slide_background_gradient(slide, DARK, NAVY_GRAD)

    day = data.get('day')
    title = data.get('title', f"Day {day}")
    subtitle = data.get('subtitle', '')
    tagline = data.get('tagline', '')

    add_text(slide, MARGIN_X, Inches(3.4), CONTENT_W, Inches(1.4),
             title, size=Pt(84), color=WHITE, bold=True,
             font=FONT_HEADING)
    if subtitle:
        add_text(slide, MARGIN_X, Inches(4.8), CONTENT_W, Inches(0.7),
                 subtitle, size=Pt(28), color=AMBER, font=FONT_HEADING)
    if tagline:
        add_text(slide, MARGIN_X, Inches(5.6), CONTENT_W, Inches(0.5),
                 tagline, size=Pt(18), color=LIGHT, italic=True)
    _maybe_speaker_notes(slide, data)
    return slide


def render_divider(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARKER)
    # left coral bar
    bar = add_rect(slide, 0, 0, Inches(0.4), SLIDE_H,
                   fill=CORAL, line=None, rounded=False)

    # chapter progress ribbon (wayfinder)
    ch = data.get('chapter')
    if ch:
        ch_total = data.get('chapter_total', 5)
        ch_label = data.get('chapter_label', '')
        crumb = f"CHAPTER {ch} OF {ch_total}"
        if ch_label:
            crumb += f" · {ch_label}"
        add_text(slide, MARGIN_X + Inches(0.4), Inches(1.0),
                 Inches(9.5), Inches(0.3), crumb.upper(),
                 size=Pt(11), color=MUTED, bold=True, font=FONT_BODY)
        seg_w = Inches(0.7)
        for i in range(ch_total):
            add_rect(slide, MARGIN_X + Inches(0.4) + (seg_w + Inches(0.12)) * i,
                     Inches(1.4), seg_w, Inches(0.09),
                     fill=ACCENT if i < ch else CARD_HI, line=None, corner=0.5)

    # Big module number
    num = data.get('module_number', '')
    title = data.get('title', '')
    time = data.get('time', '')
    subtitle = data.get('subtitle', '')

    # Module glyph — top-right corner. Smaller + a defined right margin so
    # the title can wrap into the remaining left column without colliding.
    icon_name = data.get('icon')
    if not icon_name and num != '':
        try:
            n = int(str(num).strip())
            icon_name = f'module-{n:02d}'
        except (ValueError, TypeError):
            pass
    icon_size = Inches(1.8)
    icon_right_pad = Inches(0.6)
    title_max_w = SLIDE_W - (MARGIN_X + Inches(0.4)) - icon_size - icon_right_pad - Inches(0.3)
    if icon_name:
        _add_icon(slide, icon_name,
                  SLIDE_W - icon_right_pad - icon_size,
                  Inches(1.6),
                  icon_size, icon_size)
    else:
        title_max_w = CONTENT_W

    if num != '':
        add_text(slide, MARGIN_X + Inches(0.4), Inches(1.8),
                 title_max_w, Inches(1.1),
                 f"Module {num}",
                 size=Pt(28), color=AMBER, bold=True, font=FONT_HEADING)
    # Shrink the title font when it's long so a 2-line wrap always fits
    # within the icon-constrained width and the available height.
    title_len = len(title)
    if title_len <= 22:
        title_size = Pt(56)
    elif title_len <= 30:
        title_size = Pt(46)
    elif title_len <= 42:
        title_size = Pt(38)
    else:
        title_size = Pt(32)
    add_text(slide, MARGIN_X + Inches(0.4), Inches(2.5),
             title_max_w, Inches(2.2),
             title, size=title_size, color=WHITE, bold=True,
             font=FONT_HEADING, line_spacing=1.0)
    if subtitle:
        add_text(slide, MARGIN_X + Inches(0.4), Inches(4.6),
                 CONTENT_W, Inches(0.6),
                 subtitle, size=Pt(22), color=LIGHT, italic=True)
    if time:
        add_text(slide, MARGIN_X + Inches(0.4), Inches(5.4),
                 CONTENT_W, Inches(0.5),
                 time, size=Pt(18), color=MUTED, italic=True)

    # bottom accent strip — full width, behind watermark
    accent = add_rect(slide, 0, SLIDE_H - Inches(0.08),
                      SLIDE_W, Inches(0.08),
                      fill=AMBER, line=None, rounded=False)
    _maybe_speaker_notes(slide, data)
    return slide


def render_objectives(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', 'Learning Objectives'),
                        data.get('subtitle'))
    add_bg_accent(slide, accent, data)

    items = data.get('items', [])[:6]
    top, band_h = content_band()
    n = max(len(items), 1)
    row_h = min(Inches(1.0), band_h / n)
    block_h = row_h * n
    y0 = top + (band_h - block_h) / 2
    chip = Inches(0.6)
    for i, item in enumerate(items):
        y = y0 + row_h * i
        cy = y + (row_h - chip) / 2
        c = add_rect(slide, MARGIN_X, cy, chip, chip, fill=accent, line=None,
                     corner=0.25)
        add_text(slide, MARGIN_X, cy, chip, chip,
                 str(i + 1), size=Pt(22), color=ON_PRIMARY, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)
        add_text(slide, MARGIN_X + chip + Inches(0.4), y,
                 CONTENT_W - chip - Inches(0.4), row_h,
                 item, size=Pt(19), color=LIGHT,
                 anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)

    _maybe_speaker_notes(slide, data)
    return slide


def render_content(prs, data):
    """Two-column content with headings + bullets."""
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))

    columns = data.get('columns', [])
    n = len(columns) or 1
    gap = Inches(0.35)
    col_w = (CONTENT_W - gap * (n - 1)) / n
    top, col_h = content_band()
    head_h = Inches(0.72)
    tones = [CARD, CARD_HI]

    for i, col in enumerate(columns):
        x = MARGIN_X + (col_w + gap) * i
        add_rect(slide, x, top, col_w, col_h, fill=tones[i % 2], line=None,
                 corner=0.035)
        add_rect(slide, x, top, col_w, head_h, fill=accent, line=None,
                 rounded=False)
        heading_x = x + Inches(0.3)
        heading_w = col_w - Inches(0.6)
        icon = col.get('icon')
        if _icon_path(icon):
            ic_size = Inches(0.5)
            _add_icon(slide, icon, x + Inches(0.3),
                      top + (head_h - ic_size) / 2, ic_size, ic_size)
            heading_x = x + Inches(0.3) + ic_size + Inches(0.2)
            heading_w = col_w - Inches(0.6) - ic_size - Inches(0.2)
        add_text(slide, heading_x, top, heading_w, head_h,
                 col.get('heading', ''),
                 size=SZ_H3, color=ON_PRIMARY, bold=True, font=FONT_HEADING,
                 anchor=MSO_ANCHOR.MIDDLE)
        items = col.get('items', [])
        lines = [{'text': it, 'bullet': '▸', 'bullet_color': accent,
                  'size': SZ_BODY, 'color': LIGHT}
                 for it in items[:7]]
        add_multi_text(slide, x + Inches(0.3), top + head_h + Inches(0.28),
                       col_w - Inches(0.6), col_h - head_h - Inches(0.5),
                       lines, default_size=SZ_BODY, line_spacing=1.4,
                       shrink_to_fit=True)

    _maybe_speaker_notes(slide, data)
    return slide


def render_bullets(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))
    add_bg_accent(slide, accent, data)

    items = data.get('items', [])[:7]
    top, band_h = content_band()
    n = max(len(items), 1)
    row_h = band_h / n
    num_w = Inches(1.05)
    text_x = MARGIN_X + num_w + Inches(0.15)
    text_w = CONTENT_W - num_w - Inches(0.15)
    for i, it in enumerate(items):
        ry = top + row_h * i
        add_text(slide, MARGIN_X, ry, num_w, row_h,
                 f"{i + 1:02d}", size=Pt(34), color=accent, bold=True,
                 font=FONT_HEADING, anchor=MSO_ANCHOR.MIDDLE)
        add_text(slide, text_x, ry, text_w, row_h,
                 it, size=Pt(19), color=LIGHT, anchor=MSO_ANCHOR.MIDDLE,
                 line_spacing=1.2)
        if i < n - 1:
            add_rect(slide, text_x, ry + row_h - Inches(0.012),
                     text_w, Inches(0.018), fill=CARD_HI, line=None,
                     rounded=False)
    _maybe_speaker_notes(slide, data)
    return slide


def render_diagram(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))

    dt = data.get('diagram_type', 'flow')
    if dt == 'flow':
        render_flow(slide, data.get('steps', []),
                    highlight_index=data.get('highlight_index'),
                    accent=accent, caption=data.get('caption'))
    elif dt == 'architecture':
        render_architecture(slide, data.get('rows', []),
                            caption=data.get('caption'), accent=accent)
    elif dt == 'sequence':
        render_sequence(slide, data.get('actors', ['A', 'B']),
                        data.get('messages', []), accent=accent)
    elif dt == 'comparison':
        left = dict(data.get('left', {}))
        right = dict(data.get('right', {}))
        # Neutral by default — red/green is reserved for true safety/quality
        # contrasts, which opt in by setting variant: good/bad in the YAML.
        if 'variant' not in left and 'variant' not in right:
            left['variant'] = 'neutral'
            right['variant'] = 'neutral'
        render_comparison(slide, left, right)
    elif dt == 'metrics':
        render_metrics(slide, data.get('cards', []), accent=accent)
    elif dt == 'decision':
        render_decision(slide, data.get('nodes', []), accent=accent)
    elif dt == 'quadrant':
        render_quadrant(slide, x_axis=data.get('x_axis', ''),
                        y_axis=data.get('y_axis', ''),
                        quadrants=data.get('quadrants', []), accent=accent)
    elif dt == 'd2':
        import diagram_engines as de
        out = de.cache_path('d2', data.get('d2', ''))
        if not os.path.exists(out):
            de.render_d2(data.get('d2', ''), out)
        _embed_diagram(slide, out)
    elif dt == 'chart':
        import diagram_engines as de
        spec = data.get('chart', {})
        out = de.cache_path('chart', spec)
        if not os.path.exists(out):
            de.render_chart(spec, out)
        _embed_diagram(slide, out)
    _maybe_speaker_notes(slide, data)
    return slide


def render_chart(prs, data):
    """Native PowerPoint graph: bar, donut, or progress rows."""
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))
    add_bg_accent(slide, accent, data)

    kind = data.get('chart_type', 'bar')
    top, band_h = content_band()
    series = data.get('series', [])
    labels = [str(s.get('label', '')) for s in series]
    values = [s.get('value', 0) for s in series]

    if kind == 'bar':
        add_bar_chart(slide, MARGIN_X, top, CONTENT_W, band_h,
                      labels, values, accent,
                      value_suffix=data.get('value_suffix', ''))
    elif kind == 'donut':
        chart_w = Inches(7.6)
        add_donut_chart(slide, MARGIN_X, top, chart_w, band_h,
                        labels, values, accent)
        note = data.get('note')
        if note:
            add_text(slide, MARGIN_X + chart_w + Inches(0.2),
                     top + band_h / 2 - Inches(0.6),
                     CONTENT_W - chart_w - Inches(0.2), Inches(1.2),
                     note, size=SZ_BODY, color=LIGHT, line_spacing=1.35,
                     anchor=MSO_ANCHOR.MIDDLE)
    elif kind == 'progress':
        rows = [{'label': s.get('label', ''), 'pct': s.get('value', 0),
                 'value': s.get('display', f"{s.get('value', 0)}%")}
                for s in series]
        n = max(len(rows), 1)
        row_h = Inches(0.5)
        usable = band_h - Inches(0.2)
        gap = min(Inches(0.85), max(Inches(0.32),
                  (usable - row_h * n) / max(n - 1, 1)))
        add_progress_rows(slide, MARGIN_X + Inches(0.2), top + Inches(0.1),
                          CONTENT_W - Inches(0.4), rows, accent,
                          row_h=row_h, gap=gap)
    _maybe_speaker_notes(slide, data)
    return slide


def render_terminal(prs, data):
    """Styled mac-terminal window — shows real CLI sessions as the product."""
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))

    lines = data.get('lines', [])
    side = data.get('side')
    lsp = 1.4
    band_top, band_h = content_band()
    caption = data.get('caption', '')
    cap_reserve = Inches(0.55) if caption else Inches(0)
    avail_h = band_h - cap_reserve

    # A rail fixes the window to the left column; without one the window is
    # sized to its longest line so it reads as a block, not a stretched bar.
    if side:
        win_w, side_x, side_w = split_band()
    else:
        longest = max((len(l.get('text', '')) for l in lines), default=24) + 3
        win_w = Inches(longest * 15 * 0.6 / 72.0 + 1.1)
        win_w = int(max(Inches(6.8), min(win_w, CONTENT_W)))

    bar_h = Inches(0.42)
    pad = Inches(0.36)
    text_w_in = (win_w - Inches(0.7)) / 914400.0
    text_h_cap = (avail_h - bar_h - pad) / 914400.0
    fpt, text_h_in = fit_block([l.get('text', '') for l in lines],
                               text_w_in, text_h_cap,
                               (15, 14, 13, 12, 11, 10), lsp)
    fsize = Pt(fpt)
    win_h = bar_h + Inches(text_h_in) + pad
    if side:
        win_h = max(win_h, measure_side_rail(side, side_w))
    win_h = int(min(win_h, avail_h))
    win_x = MARGIN_X
    win_y = int(optical_top(band_top, avail_h, win_h))
    if side:
        render_side_rail(slide, side_x, win_y, side_w, win_h, side, accent)
    content_top = window_chrome(slide, win_x, win_y, win_w, win_h,
                                title=data.get('window', 'claude — zsh'),
                                accent=accent)

    tlines = []
    for l in lines:
        t = l.get('t', 'out')
        txt = l.get('text', '')
        if t == 'cmd':
            # '›' over a fancier chevron on purpose: it exists in every font
            # the deck can fall back to, so a substituted prompt glyph cannot
            # inflate the line box and push the last lines out of the window.
            tlines.append({'text': txt, 'bullet': '›', 'bullet_color': accent,
                           'font': FONT_MONO, 'size': fsize, 'color': WHITE,
                           'bold': True})
        elif t == 'comment':
            tlines.append({'text': txt, 'font': FONT_MONO, 'size': fsize,
                           'color': TEXT_MUTED, 'italic': True})
        elif t == 'ok':
            tlines.append({'text': txt, 'font': FONT_MONO, 'size': fsize,
                           'color': GREEN})
        else:
            tlines.append({'text': txt, 'font': FONT_MONO, 'size': fsize,
                           'color': LIGHT})
    add_multi_text(slide, win_x + Inches(0.4), content_top + Inches(0.18),
                   win_w - Inches(0.7),
                   win_y + win_h - content_top - Inches(0.3),
                   tlines, default_size=fsize, font=FONT_MONO,
                   line_spacing=lsp, shrink_to_fit=True)
    if caption:
        cap_y = min(win_y + win_h + Inches(0.18),
                    CONTENT_SAFE_BOTTOM - Inches(0.4))
        add_text(slide, MARGIN_X, cap_y, win_w if side else CONTENT_W,
                 Inches(0.4),
                 caption, size=SZ_SMALL, color=MUTED,
                 italic=True, align=PP_ALIGN.LEFT)
    _maybe_speaker_notes(slide, data)
    return slide


def render_statement(prs, data):
    """One large authored sentence — a deliberate rhythm break."""
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = accent_for(data)
    add_bg_accent(slide, accent, data)

    text = data.get('text', '')
    kicker = data.get('kicker')
    top = Inches(2.3)
    add_rect(slide, MARGIN_X, top, Inches(1.1), Inches(0.1), fill=accent,
             line=None, rounded=False)
    if kicker:
        add_text(slide, MARGIN_X, top + Inches(0.22), CONTENT_W, Inches(0.4),
                 kicker.upper(), size=Pt(13), color=accent, bold=True,
                 font=FONT_HEADING)
    sz = Pt(46) if len(text) <= 80 else (Pt(36) if len(text) <= 130 else Pt(30))
    add_text(slide, MARGIN_X, top + Inches(0.7), CONTENT_W - Inches(1.0),
             Inches(3.2), text, size=sz, color=WHITE, bold=True,
             font=FONT_HEADING, line_spacing=1.08)
    attr = data.get('attribution')
    if attr:
        add_text(slide, MARGIN_X, Inches(6.1), CONTENT_W, Inches(0.5),
                 attr, size=Pt(16), color=MUTED, italic=True)
    _maybe_speaker_notes(slide, data)
    return slide


def render_quote(prs, data):
    """Pull-quote — large quotation, rhythm break / section punctuation."""
    slide = _add_blank_slide(prs)
    set_slide_background_gradient(slide, DARKER, NAVY_GRAD)
    accent = accent_for(data)
    quote = data.get('quote') or data.get('text', '')
    author = data.get('author', '')

    add_text(slide, MARGIN_X - Inches(0.05), Inches(1.15),
             Inches(2.5), Inches(1.6),
             "“", size=Pt(130), color=accent, bold=True,
             font=FONT_HEADING)
    sz = Pt(32) if len(quote) <= 140 else Pt(26)
    add_text(slide, MARGIN_X + Inches(0.3), Inches(2.5),
             CONTENT_W - Inches(0.8), Inches(3.0),
             quote, size=sz, color=LIGHT, italic=True, font=FONT_HEADING,
             line_spacing=1.25, anchor=MSO_ANCHOR.TOP)
    if author:
        add_text(slide, MARGIN_X + Inches(0.3), Inches(5.9),
                 CONTENT_W - Inches(0.8), Inches(0.5),
                 "— " + author, size=Pt(18), color=accent, bold=True,
                 font=FONT_HEADING)
    _maybe_speaker_notes(slide, data)
    return slide


def render_code(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))

    code = data.get('code', '')
    lang = data.get('language', '')
    caption = data.get('caption', '')

    side = data.get('side')
    code_lines = code.rstrip('\n').split('\n')
    if len(code_lines) > 36:
        code_lines = code_lines[:36] + ['…']
    ls = 1.3

    band_top, band_h = content_band()
    cap_reserve = Inches(0.55) if caption else Inches(0)
    avail_h = band_h - cap_reserve

    # size the card to the code so it reads as a block, not a wide void
    if side:
        panel_w, side_x, side_w = split_band()
    else:
        longest = max((len(l) for l in code_lines), default=10)
        panel_w = Inches(longest * 14 * 0.6 / 72.0 + 0.9)
        panel_w = int(max(Inches(5.2), min(panel_w, CONTENT_W)))

    pad = Inches(0.5)
    fpt, text_h_in = fit_block(code_lines,
                               (panel_w - Inches(0.6)) / 914400.0,
                               (avail_h - pad) / 914400.0,
                               (14, 13, 12, 11, 10, 9), ls)
    fsize = Pt(fpt)
    panel_h = Inches(text_h_in) + pad
    if side:
        panel_h = max(panel_h, measure_side_rail(side, side_w))
    panel_h = int(min(panel_h, avail_h))
    panel_x = MARGIN_X
    panel_y = int(optical_top(band_top, avail_h, panel_h))
    if side:
        render_side_rail(slide, side_x, panel_y, side_w, panel_h, side, accent)

    add_rect(slide, panel_x, panel_y, panel_w, panel_h, fill=CODE_BG,
             line=None, corner=0.03)
    add_rect(slide, panel_x, panel_y, Inches(0.1), panel_h, fill=accent,
             line=None, rounded=False)
    if lang:
        label = lang.upper()
        pill_w = Inches(max(1.0, min(2.4, 0.16 * len(label) + 0.6)))
        add_rect(slide, panel_x + Inches(0.25), panel_y - Inches(0.18),
                 pill_w, Inches(0.36), fill=accent, line=None)
        add_text(slide, panel_x + Inches(0.25), panel_y - Inches(0.18),
                 pill_w, Inches(0.36),
                 label, size=Pt(12), color=ON_PRIMARY, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)

    text_lines = [{'text': line if line else ' ', 'font': FONT_MONO,
                   'size': fsize, 'color': LIGHT} for line in code_lines]
    add_multi_text(slide,
                   panel_x + Inches(0.4), panel_y + Inches(0.25),
                   panel_w - Inches(0.6), panel_h - Inches(0.45),
                   text_lines, default_size=fsize,
                   font=FONT_MONO, line_spacing=ls, shrink_to_fit=True)

    if caption:
        cap_y = min(panel_y + panel_h + Inches(0.18),
                    CONTENT_SAFE_BOTTOM - Inches(0.4))
        add_text(slide, MARGIN_X, cap_y, panel_w if side else CONTENT_W,
                 Inches(0.4),
                 caption, size=SZ_SMALL, color=MUTED,
                 italic=True, align=PP_ALIGN.LEFT)
    _maybe_speaker_notes(slide, data)
    return slide


def render_table(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))

    headers = data.get('headers', [])
    rows = data.get('rows', [])
    cols = len(headers)
    if cols == 0:
        _maybe_speaker_notes(slide, data)
        return slide

    band_top, band_h = content_band()
    n_rows = min(len(rows), 9) + 1
    row_h = int(min(Inches(0.72), band_h / n_rows))
    table_h = row_h * n_rows
    table_x = int(MARGIN_X)
    table_w = int(CONTENT_W)
    table_y = int(band_top + (band_h - table_h) / 2)

    shp = slide.shapes.add_table(n_rows, cols, table_x, table_y,
                                 table_w, table_h)
    tbl = shp.table
    # header row
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = accent
        tf = cell.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = str(h)
        r.font.name = FONT_HEADING
        r.font.size = Pt(14)
        r.font.color.rgb = ON_PRIMARY
        r.font.bold = True
        cell.margin_left = Inches(0.15)
        cell.margin_right = Inches(0.15)
        cell.margin_top = Inches(0.08)
        cell.margin_bottom = Inches(0.08)

    # body rows
    for i, row in enumerate(rows[: 9]):  # cap at 9 body rows
        for j, val in enumerate(row[: cols]):
            cell = tbl.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = PANEL_BG if (i % 2 == 0) else DARKER
            tf = cell.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = str(val)
            r.font.name = FONT_BODY
            r.font.size = Pt(13)
            r.font.color.rgb = LIGHT
            cell.margin_left = Inches(0.15)
            cell.margin_right = Inches(0.15)
            cell.margin_top = Inches(0.06)
            cell.margin_bottom = Inches(0.06)

    _maybe_speaker_notes(slide, data)
    return slide


def render_callout(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    accent = add_header(slide, data, data.get('title', ''), data.get('subtitle'))
    add_bg_accent(slide, accent, data)

    text = data.get('text', '')
    band_top, band_h = content_band()
    box_w = Inches(11.0)
    box_h = min(Inches(3.6), band_h)
    box_x = MARGIN_X + (CONTENT_W - box_w) / 2
    box_y = optical_top(band_top, band_h, box_h)
    add_rect(slide, box_x, box_y, box_w, box_h, fill=CARD, line=None,
             corner=0.04)
    add_rect(slide, box_x, box_y, Inches(0.16), box_h,
             fill=accent, line=None, rounded=False)
    add_text(slide, box_x + Inches(0.7), box_y + Inches(0.3),
             box_w - Inches(1.1), box_h - Inches(0.6),
             text, size=Pt(23), color=LIGHT,
             anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.3)
    _maybe_speaker_notes(slide, data)
    return slide


def render_lab(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background_gradient(slide, DARKER, DARK)
    # left amber bar (lab indicator)
    add_rect(slide, 0, 0, Inches(0.4), SLIDE_H,
             fill=AMBER, line=None, rounded=False)

    title = data.get('title', 'Lab')
    duration = data.get('duration', '')
    add_text(slide, MARGIN_X + Inches(0.4), TITLE_TOP,
             Inches(1.4), Inches(0.5),
             "▶ LAB", size=Pt(16), color=AMBER, bold=True,
             font=FONT_HEADING)
    t_sz = Pt(30) if len(title) <= 38 else Pt(25)
    add_text(slide, MARGIN_X + Inches(0.4), TITLE_TOP + Inches(0.4),
             Inches(8.7), Inches(0.7),
             title, size=t_sz, color=WHITE, bold=True, font=FONT_HEADING)
    if duration:
        pill_w = Inches(1.7)
        pill_x = SLIDE_W - MARGIN_X - pill_w
        add_rect(slide, pill_x, TITLE_TOP + Inches(0.45), pill_w, Inches(0.46),
                 fill=CARD_HI, line=None, corner=0.5)
        add_text(slide, pill_x, TITLE_TOP + Inches(0.45), pill_w, Inches(0.46),
                 duration, size=Pt(15), color=AMBER, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)

    steps = data.get('steps', [])
    panel_w = Inches(11.0)
    panel_x = MARGIN_X + Inches(0.4) + (CONTENT_W - panel_w - Inches(0.4)) / 2
    panel_y = BODY_TOP + Inches(0.3)
    panel_h = Inches(0.7) * len(steps) + Inches(0.5)
    if panel_h > Inches(4.5):
        panel_h = Inches(4.5)
    add_rect(slide, panel_x, panel_y, panel_w, panel_h,
             fill=PANEL_BG, line=None)

    inner_y = panel_y + Inches(0.25)
    for i, step in enumerate(steps[:6]):
        y = inner_y + Inches(0.7) * i
        chip = add_rect(slide, panel_x + Inches(0.3), y,
                        Inches(0.5), Inches(0.5),
                        fill=AMBER, line=None)
        add_text(slide, panel_x + Inches(0.3), y,
                 Inches(0.5), Inches(0.5),
                 str(i + 1), size=Pt(16), color=DARK, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)
        add_text(slide, panel_x + Inches(1.0), y,
                 panel_w - Inches(1.3), Inches(0.55),
                 step, size=Pt(16), color=LIGHT,
                 anchor=MSO_ANCHOR.MIDDLE)

    outcome = data.get('outcome', '')
    if outcome:
        out_h = Inches(0.5)
        out_y = min(panel_y + panel_h + Inches(0.2),
                    CONTENT_SAFE_BOTTOM - out_h)
        add_text(slide, panel_x, out_y, Inches(1.4), out_h,
                 "Outcome:", size=Pt(15), color=AMBER, bold=True)
        add_text(slide, panel_x + Inches(1.5), out_y,
                 panel_w - Inches(1.6), out_h,
                 outcome, size=Pt(15), color=WHITE)
    _maybe_speaker_notes(slide, data)
    return slide


def render_discussion(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background_gradient(slide, DARKER, NAVY_GRAD)
    # left coral bar
    add_rect(slide, 0, 0, Inches(0.4), SLIDE_H,
             fill=CORAL, line=None, rounded=False)

    add_text(slide, MARGIN_X + Inches(0.4), Inches(1.0),
             CONTENT_W, Inches(0.5),
             "DISCUSS", size=Pt(18), color=CORAL, bold=True,
             font=FONT_HEADING)
    add_text(slide, MARGIN_X + Inches(0.4), Inches(1.5),
             CONTENT_W, Inches(0.9),
             data.get('title', 'Discussion'),
             size=Pt(34), color=WHITE, bold=True, font=FONT_HEADING)

    prompt = data.get('prompt', '')
    add_text(slide, MARGIN_X + Inches(0.4) + Inches(0.5), Inches(3.0),
             CONTENT_W - Inches(1.0), Inches(3.0),
             f"“{prompt}”", size=Pt(28), color=LIGHT,
             italic=True, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.CENTER)
    _maybe_speaker_notes(slide, data)
    return slide


def render_takeaways(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background_gradient(slide, DARK, NAVY_GRAD)
    accent = add_header(slide, data, data.get('title', 'Key Takeaways'),
                        data.get('subtitle'))

    items = data.get('items', [])[:5]
    top, band_h = content_band()
    n = max(len(items), 1)
    gap = Inches(0.22)
    row_h = min(Inches(0.95), (band_h - gap * (n - 1)) / n)
    block_h = row_h * n + gap * (n - 1)
    y0 = top + (band_h - block_h) / 2
    chip = Inches(0.6)

    for i, item in enumerate(items):
        y = y0 + (row_h + gap) * i
        add_rect(slide, MARGIN_X, y, CONTENT_W, row_h, fill=CARD, line=None,
                 corner=0.05)
        chip_y = y + (row_h - chip) / 2
        c = add_rect(slide, MARGIN_X + Inches(0.25), chip_y, chip, chip,
                     fill=accent, line=None, corner=0.25)
        add_text(slide, MARGIN_X + Inches(0.25), chip_y, chip, chip,
                 "✓", size=Pt(22), color=ON_PRIMARY, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)
        add_text(slide, MARGIN_X + chip + Inches(0.55), y,
                 CONTENT_W - chip - Inches(0.85), row_h,
                 item, size=Pt(18), color=LIGHT,
                 anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
    _maybe_speaker_notes(slide, data)
    return slide


def render_chapter_opener(prs, data):
    slide = _add_blank_slide(prs)
    num = data.get('chapter')
    art = None
    if num:
        cand = os.path.join(IMAGES_DIR, f'chapter_art_{num}.png')
        if os.path.exists(cand):
            art = cand
    if not art:
        cand = os.path.join(IMAGES_DIR, 'chapter_art.png')
        art = cand if os.path.exists(cand) else None
    if art:
        slide.shapes.add_picture(art, 0, 0, width=SLIDE_W, height=SLIDE_H)
    else:
        set_slide_background_gradient(slide, DARK, NAVY_GRAD)

    label = data.get('label', 'Chapter')
    title = data.get('title', '')
    accent_line = data.get('accent_line', '')
    subtitle = data.get('subtitle', '')

    add_text(slide, MARGIN_X, Inches(0.5), CONTENT_W, Inches(0.35),
             "FAST LANE · CLAUDE CODE MASTERCLASS", size=Pt(11),
             color=MUTED, bold=True, font=FONT_BODY)
    add_text(slide, MARGIN_X, Inches(2.3), Inches(10.0), Inches(0.45),
             label.upper(), size=Pt(16), color=ACCENT, bold=True,
             font=FONT_HEADING)
    add_rect(slide, MARGIN_X, Inches(2.98), Inches(0.9), Inches(0.045),
             fill=ACCENT, line=None, rounded=False)
    title_size = Pt(56) if len(title) <= 18 else Pt(44)
    add_text(slide, MARGIN_X, Inches(3.15), Inches(10.0), Inches(1.1),
             title, size=title_size, color=WHITE, bold=True,
             font=FONT_HEADING, line_spacing=1.0)
    if accent_line:
        add_text(slide, MARGIN_X, Inches(4.35), Inches(10.0), Inches(0.9),
                 accent_line, size=Pt(34), color=PRIMARY, bold=True,
                 font=FONT_HEADING)
    if subtitle:
        add_text(slide, MARGIN_X, Inches(5.55), Inches(10.5), Inches(0.6),
                 subtitle, size=Pt(17), color=MUTED, italic=True,
                 font=FONT_BODY)
    _brandmark(slide, SLIDE_W - Inches(3.0), SLIDE_H - Inches(0.95),
               Inches(2.1), Inches(0.45), size=Pt(22))
    _maybe_speaker_notes(slide, data)
    return slide


def render_chapter_contents(prs, data):
    slide = _add_blank_slide(prs)
    set_slide_background(slide, DARK)
    add_text(slide, MARGIN_X, Inches(0.95), CONTENT_W, Inches(0.55),
             data.get('title', ''), size=Pt(34), color=WHITE, bold=True,
             font=FONT_HEADING)
    add_rect(slide, MARGIN_X, Inches(1.72), Inches(0.9), Inches(0.045),
             fill=PRIMARY, line=None, rounded=False)
    add_text(slide, MARGIN_X, Inches(1.9), CONTENT_W, Inches(0.4),
             "IN THIS CHAPTER", size=Pt(12), color=PRIMARY, bold=True,
             font=FONT_BODY)

    items = data.get('items', [])[:4]
    n = max(len(items), 1)
    top = Inches(2.55)
    avail = Inches(4.1)
    gap = Inches(0.28)
    rh = min(Inches(1.5), (avail - gap * (n - 1)) / n)
    # adapt type + positions so tight rows (4-module chapters) never crowd
    big = rh >= Inches(1.15)
    num_sz = Pt(40) if big else Pt(30)
    title_sz = Pt(22) if big else Pt(19)
    desc_sz = Pt(14) if big else Pt(13)
    for i, it in enumerate(items):
        y = top + (rh + gap) * i
        add_rect(slide, MARGIN_X, y, CONTENT_W, rh, fill=PANEL_BG,
                 line=None, corner=0.05)
        add_rect(slide, MARGIN_X, y, Inches(0.12), rh, fill=ACCENT,
                 line=None, rounded=False)
        add_text(slide, MARGIN_X + Inches(0.45), y, Inches(1.7), rh,
                 str(it.get('num', '')), size=num_sz, color=PRIMARY,
                 bold=True, font=FONT_HEADING, anchor=MSO_ANCHOR.MIDDLE)
        lines = [{'text': it.get('title', ''), 'size': title_sz,
                  'color': WHITE, 'bold': True, 'font': FONT_HEADING}]
        if it.get('desc'):
            lines.append({'text': it.get('desc', ''), 'size': desc_sz,
                          'color': MUTED, 'font': FONT_BODY})
        add_multi_text(slide, MARGIN_X + Inches(2.2), y + Inches(0.1),
                       CONTENT_W - Inches(2.6), rh - Inches(0.2),
                       lines, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05,
                       shrink_to_fit=True)
    _maybe_speaker_notes(slide, data)
    return slide


def render_closing_cta(prs, data):
    slide = _add_blank_slide(prs)
    art = next((p for p in (
        os.path.join(IMAGES_DIR, 'closing_bg.png'),
        os.path.join(IMAGES_DIR, 'chapter_art.png')) if os.path.exists(p)), None)
    if art:
        slide.shapes.add_picture(art, 0, 0, width=SLIDE_W, height=SLIDE_H)
    else:
        set_slide_background_gradient(slide, DARK, NAVY_GRAD)
    add_text(slide, MARGIN_X, Inches(1.6), CONTENT_W, Inches(0.4),
             data.get('kicker', "THAT'S A WRAP"), size=Pt(13), color=ACCENT,
             bold=True, font=FONT_BODY)
    add_rect(slide, MARGIN_X, Inches(2.15), Inches(0.9), Inches(0.045),
             fill=ACCENT, line=None, rounded=False)
    add_text(slide, MARGIN_X, Inches(2.35), Inches(11.0), Inches(1.1),
             data.get('title', 'Now go build.'), size=Pt(56), color=WHITE,
             bold=True, font=FONT_HEADING)
    sub = data.get('subtitle', '')
    if sub:
        add_text(slide, MARGIN_X, Inches(3.8), Inches(10.5), Inches(1.0),
                 sub, size=Pt(20), color=PRIMARY, font=FONT_BODY,
                 line_spacing=1.3)
    btns = data.get('buttons', [])
    bx = MARGIN_X
    for i, b in enumerate(btns[:3]):
        bw = Inches(0.18 * len(b) + 0.9)
        fill = ACCENT if i == 0 else CARD_HI
        tcol = DARK if i == 0 else PRIMARY
        add_rect(slide, bx, Inches(5.4), bw, Inches(0.62), fill=fill,
                 line=None, corner=0.12)
        add_text(slide, bx, Inches(5.4), bw, Inches(0.62), b, size=Pt(16),
                 color=tcol, bold=True, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=FONT_HEADING)
        bx = bx + bw + Inches(0.3)
    _brandmark(slide, SLIDE_W - Inches(3.0), SLIDE_H - Inches(0.95),
               Inches(2.1), Inches(0.45), size=Pt(22))
    _maybe_speaker_notes(slide, data)
    return slide


def _maybe_speaker_notes(slide, data):
    notes = data.get('notes', '')
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
