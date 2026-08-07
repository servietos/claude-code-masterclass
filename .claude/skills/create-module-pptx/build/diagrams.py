"""Reusable diagram renderers — flow, architecture, sequence, comparison, metrics, decision, quadrant."""

from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from theme import (
    CORAL, AMBER, GOLD, DARK, DARKER, PANEL_BG, LIGHT, MUTED, WHITE,
    GREEN, RED, BAD_BG, GOOD_BG, NAVY_GRAD, ON_PRIMARY, CARD, CARD_HI,
    PRIMARY, FONT_HEADING, FONT_BODY, FONT_MONO,
    SLIDE_W, SLIDE_H, MARGIN_X, CONTENT_W, BODY_TOP, BODY_H,
    CONTENT_SAFE_BOTTOM,
    SZ_BODY, SZ_SMALL, SZ_TINY, SZ_H3, SZ_CARD_NUMBER, SZ_CARD_LABEL,
)
from helpers import (
    add_rect, add_text, add_multi_text, add_arrow, set_solid_fill,
    set_line, truncate,
)
from design import optical_top


def render_flow(slide, steps, *, highlight_index=None, top=None, height=None,
                accent=CORAL, caption=None):
    """Render a horizontal flow of step boxes with arrows, vertically centered
    in the content frame so single-row flows don't leave a void.

    Falls back to two rows if more than 5 steps.
    """
    n = len(steps)
    if n == 0:
        return

    rows = [steps] if n <= 5 else [steps[: (n + 1) // 2], steps[(n + 1) // 2:]]
    available_w = CONTENT_W
    box_h = Inches(1.3)
    row_pitch = Inches(2.0)
    arrow_w = Inches(0.4)

    band_top = BODY_TOP + Inches(0.35)
    band_h = CONTENT_SAFE_BOTTOM - band_top
    block_h = box_h + row_pitch * (len(rows) - 1)
    if caption:
        block_h += Inches(0.5)
    top = top or optical_top(band_top, band_h, block_h)

    for r, row in enumerate(rows):
        m = len(row)
        total_arrow_w = arrow_w * (m - 1)
        box_w = (available_w - total_arrow_w) / m
        if box_w > Inches(2.7):
            box_w = Inches(2.7)
        row_total_w = box_w * m + total_arrow_w
        start_x = MARGIN_X + (CONTENT_W - row_total_w) / 2
        y = top + row_pitch * r
        for i, step in enumerate(row):
            absolute_idx = i if r == 0 else i + len(rows[0])
            x = start_x + (box_w + arrow_w) * i
            is_hi = (highlight_index == absolute_idx)
            fill = accent if is_hi else CARD
            box = add_rect(slide, x, y, box_w, box_h, fill=fill, line=None,
                           corner=0.06)
            if not is_hi:
                add_rect(slide, x, y, box_w, Inches(0.08), fill=accent,
                         line=None, rounded=False)
            # A step is either a plain string or {label, desc}. The dict form
            # renders the label bold above a smaller description line.
            if isinstance(step, dict):
                label, desc = step.get('label', ''), step.get('desc', '')
            else:
                label, desc = str(step), ''
            fg = ON_PRIMARY if is_hi else LIGHT
            if desc:
                lines = [
                    {'text': label, 'size': SZ_SMALL, 'color': fg, 'bold': True},
                    {'text': desc, 'size': SZ_TINY,
                     'color': fg if is_hi else MUTED},
                ]
                add_multi_text(slide, x + Inches(0.1), y + Inches(0.1),
                               box_w - Inches(0.2), box_h - Inches(0.2),
                               lines, align=PP_ALIGN.CENTER,
                               anchor=MSO_ANCHOR.MIDDLE, font=FONT_HEADING,
                               line_spacing=1.1, shrink_to_fit=True)
            else:
                add_text(slide, x + Inches(0.1), y + Inches(0.1),
                         box_w - Inches(0.2), box_h - Inches(0.2),
                         label, size=SZ_SMALL,
                         color=fg,
                         bold=is_hi,
                         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                         font=FONT_HEADING)
            if i < m - 1:
                ax1 = x + box_w + Inches(0.05)
                ax2 = x + box_w + arrow_w - Inches(0.05)
                ay = y + box_h / 2
                add_arrow(slide, ax1, ay, ax2, ay, color=accent, width_pt=2.5)

    if caption:
        cap_y = top + block_h - Inches(0.4)
        add_text(slide, MARGIN_X, cap_y, CONTENT_W, Inches(0.5),
                 caption, size=SZ_SMALL, color=MUTED,
                 italic=True, align=PP_ALIGN.CENTER)


def render_architecture(slide, rows, *, caption=None, top=None, accent=CORAL):
    """Render rows of architecture boxes, vertically centered in the frame."""
    n_rows = len(rows)
    band_top = BODY_TOP + Inches(0.35)
    band_h = CONTENT_SAFE_BOTTOM - band_top
    available_h = band_h - (Inches(0.5) if caption else Inches(0))
    base_row_h = Inches(1.15)
    base_gap = Inches(0.3)
    needed = base_row_h * n_rows + base_gap * max(n_rows - 1, 0)
    if needed > available_h and n_rows > 0:
        scale = available_h / needed
        row_h = int(base_row_h * scale)
        row_gap = int(base_gap * scale)
    else:
        row_h = base_row_h
        row_gap = base_gap
    block_h = row_h * n_rows + row_gap * max(n_rows - 1, 0)
    top = top or optical_top(band_top, available_h, block_h)
    box_gap = Inches(0.18)

    for r_idx, row in enumerate(rows):
        m = len(row)
        if m == 0:
            continue
        # compute box widths
        wide_count = sum(1 for b in row if b.get('role') == 'wide')
        if wide_count == m:
            box_w = CONTENT_W - Inches(0.4)
            start_x = MARGIN_X + Inches(0.2)
            box_w_each = box_w
        else:
            total_gap = box_gap * (m - 1)
            box_w_each = (CONTENT_W - total_gap) / m
            start_x = MARGIN_X
        y = top + (row_h + row_gap) * r_idx
        for i, box in enumerate(row):
            role = box.get('role', 'secondary')
            label = box.get('label', '')
            x = start_x + (box_w_each + box_gap) * i
            w = box_w_each
            if role == 'primary':
                fill = accent
                text_color = ON_PRIMARY
                bold = True
            elif role == 'wide':
                fill = CARD_HI
                text_color = LIGHT
                bold = False
            else:
                fill = CARD
                text_color = LIGHT
                bold = False
            add_rect(slide, x, y, w, row_h, fill=fill, line=None)
            icon = box.get('icon')
            text_x = x + Inches(0.1)
            text_w = w - Inches(0.2)
            if icon:
                # try to resolve icon via layouts helper at runtime
                from layouts import _icon_path, _add_icon
                if _icon_path(icon):
                    icon_size = min(row_h - Inches(0.3), Inches(0.55))
                    _add_icon(slide, icon,
                              x + Inches(0.15),
                              y + (row_h - icon_size) / 2,
                              icon_size, icon_size)
                    text_x = x + Inches(0.15) + icon_size + Inches(0.15)
                    text_w = w - (text_x - x) - Inches(0.15)
            add_text(slide, text_x, y + Inches(0.1),
                     text_w, row_h - Inches(0.2),
                     label, size=SZ_SMALL, color=text_color, bold=bold,
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                     font=FONT_HEADING)
        # connectors between rows — under every column box, so the diagram
        # reads as a layered stack instead of a single-column funnel.
        if r_idx < n_rows - 1:
            ay1 = y + row_h
            ay2 = y + row_h + row_gap
            for i, _ in enumerate(row):
                ax = start_x + (box_w_each + box_gap) * i + box_w_each / 2
                add_arrow(slide, ax, ay1, ax, ay2,
                          color=accent, width_pt=2.0)

    if caption:
        cap_y = top + (row_h + row_gap) * n_rows + Inches(0.15)
        add_text(slide, MARGIN_X, cap_y, CONTENT_W, Inches(0.4),
                 caption, size=SZ_SMALL, color=MUTED,
                 italic=True, align=PP_ALIGN.CENTER)


def render_sequence(slide, actors, messages, *, top=None, accent=CORAL):
    """Render a sequence diagram (N lifelines + horizontal messages)."""
    top = top or (BODY_TOP + Inches(0.1))
    actor_h = Inches(0.5)
    n_actors = max(len(actors), 2)
    # max actor width that fits, with side padding
    side_pad = Inches(0.4)
    avail_w = CONTENT_W - side_pad * 2
    actor_w = min(Inches(2.0), int(avail_w / n_actors - Inches(0.3)))
    # space evenly: lifelines at equally-spaced centers
    gap = (avail_w - actor_w * n_actors) / max(n_actors - 1, 1)
    actor_xs = []
    actor_cxs = []
    for k in range(n_actors):
        x = MARGIN_X + side_pad + (actor_w + gap) * k
        actor_xs.append(int(x))
        actor_cxs.append(int(x + actor_w / 2))

    # actor heads (top + bottom)
    for x, name in zip(actor_xs, actors[:n_actors]):
        add_rect(slide, x, top, actor_w, actor_h, fill=accent, line=None)
        add_text(slide, x, top, actor_w, actor_h, name,
                 size=SZ_SMALL, color=ON_PRIMARY, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)

    n_msgs = len(messages)
    msg_area_top = top + actor_h + Inches(0.15)
    # keep the bottom anchor boxes clear of the footer/watermark zone
    msg_area_h = Inches(3.7)
    step = msg_area_h / max(n_msgs + 1, 2)

    # lifelines
    line_bottom_y = msg_area_top + step * (n_msgs + 0.5)
    for cx in actor_cxs:
        line = slide.shapes.add_connector(1, cx, int(msg_area_top), cx, int(line_bottom_y))
        line.line.color.rgb = MUTED
        line.line.width = Pt(1)

    # bottom anchors
    for x, name in zip(actor_xs, actors[:n_actors]):
        add_rect(slide, x, line_bottom_y, actor_w, actor_h,
                 fill=PANEL_BG, line=None)
        add_text(slide, x, line_bottom_y, actor_w, actor_h, name,
                 size=SZ_SMALL, color=LIGHT, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=FONT_HEADING)

    # actor lookup
    actor_idx = {name: i for i, name in enumerate(actors[:n_actors])}

    # messages
    for i, m in enumerate(messages, start=1):
        y = msg_area_top + step * i
        src_actor = m.get('from')
        dst_actor = m.get('to')
        src_i = actor_idx.get(src_actor, 0)
        dst_i = actor_idx.get(dst_actor, min(1, n_actors - 1))
        src = actor_cxs[src_i]
        dst = actor_cxs[dst_i]
        label = m.get('text', '')
        is_self = (src_i == dst_i)
        if is_self:
            # draw a small self-loop bracket extending to the side
            loop_w = Inches(0.6)
            # bias the loop direction toward the side with more room
            loop_right = (src_i < n_actors - 1)
            if loop_right:
                p1 = (src, y - Inches(0.18))
                p2 = (src + loop_w, y - Inches(0.18))
                p3 = (src + loop_w, y + Inches(0.18))
                p4 = (src, y + Inches(0.18))
            else:
                p1 = (src, y - Inches(0.18))
                p2 = (src - loop_w, y - Inches(0.18))
                p3 = (src - loop_w, y + Inches(0.18))
                p4 = (src, y + Inches(0.18))
            from helpers import add_arrow as _add_arrow  # local to avoid cycle
            # Use thin lines via connector (no head) for the 3 sides
            for (x1, y1), (x2, y2) in [(p1, p2), (p2, p3)]:
                conn = slide.shapes.add_connector(1, int(x1), int(y1), int(x2), int(y2))
                conn.line.color.rgb = AMBER
                conn.line.width = Pt(1.75)
            # final arrow back to lifeline
            _add_arrow(slide, p3[0], p3[1], p4[0], p4[1],
                       color=AMBER, width_pt=2.2)
            label_w = Inches(4.0)
            if loop_right:
                label_x = src + loop_w + Inches(0.1)
                align = PP_ALIGN.LEFT
            else:
                label_x = src - loop_w - label_w - Inches(0.1)
                align = PP_ALIGN.RIGHT
            add_text(slide, label_x, y - Inches(0.2),
                     label_w, Inches(0.35),
                     label, size=SZ_TINY, color=LIGHT,
                     align=align, font=FONT_MONO)
        else:
            color = AMBER if src < dst else CORAL
            add_arrow(slide, src, y, dst, y, color=color, width_pt=2.2)
            label_x = min(src, dst) + Inches(0.1)
            label_w = abs(dst - src) - Inches(0.2)
            add_text(slide, label_x, y - Inches(0.4),
                     label_w, Inches(0.35),
                     label, size=SZ_TINY, color=LIGHT,
                     align=PP_ALIGN.CENTER, font=FONT_MONO)


def render_comparison(slide, left, right, *, top=None):
    """Two side-by-side cards with header bands and a center VS divider."""
    top = top or (BODY_TOP + Inches(0.35))
    gap = Inches(0.55)
    card_w = (CONTENT_W - gap) / 2
    card_h = CONTENT_SAFE_BOTTOM - top
    head_h = Inches(0.72)

    neutral_mode = (left.get('variant') == 'neutral' or
                    right.get('variant') == 'neutral')

    for i, (data, is_left) in enumerate([(left, True), (right, False)]):
        x = MARGIN_X + (card_w + gap) * (0 if is_left else 1)
        if neutral_mode:
            # Neutral comparison: both headers teal (structure); the two cards
            # are told apart by body tone + the VS divider, not by hue, so no
            # false danger/safe reading.
            fill = CARD if is_left else CARD_HI
            accent = PRIMARY
        else:
            bad = data.get('variant', 'good' if not is_left else 'bad') == 'bad' or \
                  (is_left and data.get('variant') != 'good')
            if 'variant' in data:
                bad = data['variant'] == 'bad'
            fill = BAD_BG if bad else GOOD_BG
            accent = RED if bad else GREEN
        add_rect(slide, x, top, card_w, card_h, fill=fill, line=None,
                 corner=0.035)
        add_rect(slide, x, top, card_w, head_h, fill=accent, line=None,
                 rounded=False)
        add_text(slide, x + Inches(0.3), top, card_w - Inches(0.6), head_h,
                 data.get('heading', ''),
                 size=SZ_H3, color=DARK, bold=True, font=FONT_HEADING,
                 anchor=MSO_ANCHOR.MIDDLE)
        items = data.get('items', [])
        lines = [{'text': it, 'bullet': '▸', 'bullet_color': accent,
                  'size': SZ_BODY, 'color': LIGHT}
                 for it in items]
        add_multi_text(slide, x + Inches(0.3), top + head_h + Inches(0.3),
                       card_w - Inches(0.6), card_h - head_h - Inches(0.5),
                       lines, default_size=SZ_BODY, line_spacing=1.4,
                       shrink_to_fit=True)

    cx = MARGIN_X + card_w + gap / 2
    cy = top + card_h / 2
    chip = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                  int(cx - Inches(0.32)), int(cy - Inches(0.32)),
                                  Inches(0.64), Inches(0.64))
    set_solid_fill(chip, DARK)
    set_line(chip, MUTED, 1.25)
    chip.shadow.inherit = False
    add_text(slide, int(cx - Inches(0.4)), int(cy - Inches(0.22)),
             Inches(0.8), Inches(0.44), "VS", size=SZ_SMALL, color=MUTED,
             bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
             font=FONT_HEADING)


def render_metrics(slide, cards, *, top=None, accent=PRIMARY):
    """Big number cards, vertically centered in the frame, chapter-accented."""
    band_top = top or (BODY_TOP + Inches(0.35))
    band_h = CONTENT_SAFE_BOTTOM - band_top
    n = len(cards)
    rows = [cards] if n <= 3 else [cards[: (n + 1) // 2], cards[(n + 1) // 2:]]
    n_rows = len(rows)
    gap = Inches(0.35)
    row_gap = Inches(0.4)
    card_h = min(Inches(2.35), (band_h - row_gap * (n_rows - 1)) / n_rows)
    block_h = card_h * n_rows + row_gap * (n_rows - 1)
    y0 = optical_top(band_top, band_h, block_h)

    for r, row in enumerate(rows):
        m = len(row)
        total_gap = gap * (m - 1)
        card_w = (CONTENT_W - total_gap) / m
        if card_w > Inches(3.6):
            card_w = Inches(3.6)
        row_total = card_w * m + total_gap
        start_x = MARGIN_X + (CONTENT_W - row_total) / 2
        y = y0 + (card_h + row_gap) * r
        for i, c in enumerate(row):
            x = start_x + (card_w + gap) * i
            add_rect(slide, x, y, card_w, card_h, fill=CARD, line=None,
                     corner=0.05)
            add_rect(slide, x + Inches(0.3), y + Inches(0.28),
                     Inches(0.6), Inches(0.07), fill=accent, line=None,
                     rounded=False)
            add_text(slide, x + Inches(0.28), y + Inches(0.45),
                     card_w - Inches(0.56), card_h - Inches(1.1),
                     str(c.get('number', '')),
                     size=SZ_CARD_NUMBER, color=accent, bold=True,
                     align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE,
                     font=FONT_HEADING)
            add_text(slide, x + Inches(0.3), y + card_h - Inches(0.62),
                     card_w - Inches(0.6), Inches(0.5),
                     str(c.get('label', '')),
                     size=Pt(13), color=MUTED,
                     align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP)


def render_decision(slide, nodes, *, top=None, accent=CORAL):
    """Q/A decision tree — rows of question + answer chip, centered in frame."""
    from pptx.util import Emu
    row_h = Inches(0.8)
    n = max(len(nodes), 1)
    band_top = BODY_TOP + Inches(0.35)
    band_h = CONTENT_SAFE_BOTTOM - band_top
    row_gap = min(Inches(0.4), max(Inches(0.16),
                  (band_h - row_h * n) / max(n - 1, 1)))
    block_h = row_h * n + row_gap * (n - 1)
    top = top or optical_top(band_top, band_h, block_h)
    q_w = Emu(int(CONTENT_W * 0.62))
    a_w = Emu(int(CONTENT_W * 0.30))
    gap = Emu(int(CONTENT_W * 0.04))

    for i, node in enumerate(nodes):
        y = top + (row_h + row_gap) * i
        add_rect(slide, MARGIN_X, y, q_w, row_h, fill=CARD, line=None,
                 corner=0.08)
        add_rect(slide, MARGIN_X, y, Inches(0.1), row_h, fill=accent,
                 line=None, rounded=False)
        add_text(slide, MARGIN_X + Inches(0.3), y, q_w - Inches(0.5), row_h,
                 node.get('q', ''), size=SZ_BODY, color=LIGHT,
                 anchor=MSO_ANCHOR.MIDDLE, font=FONT_BODY)
        a_x = MARGIN_X + q_w + gap
        chip = add_rect(slide, a_x, y, a_w, row_h, fill=accent, line=None,
                        corner=0.12)
        add_text(slide, a_x, y, a_w, row_h,
                 node.get('a', ''), size=SZ_BODY, color=ON_PRIMARY,
                 bold=True, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=FONT_HEADING)


def render_quadrant(slide, *, x_axis, y_axis, quadrants, top=None, accent=CORAL):
    """2x2 matrix with axis labels."""
    top = top or (BODY_TOP + Inches(0.2))
    grid_w = Inches(8.5)
    grid_h = Inches(4.6)
    grid_x = MARGIN_X + (CONTENT_W - grid_w) / 2
    cell_w = grid_w / 2
    cell_h = grid_h / 2

    positions = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for (cx, cy), q in zip(positions, quadrants):
        x = grid_x + cell_w * cx
        y = top + cell_h * cy
        add_rect(slide, x, y, cell_w, cell_h, fill=PANEL_BG, line=None,
                 rounded=False)
        # heading gets a fixed reserved area so body never overlaps
        heading_h = Inches(0.9)
        add_text(slide, x + Inches(0.2), y + Inches(0.12),
                 cell_w - Inches(0.4), heading_h,
                 q.get('label', ''), size=Pt(15), color=accent, bold=True,
                 font=FONT_HEADING, line_spacing=1.1)
        items = q.get('items', [])
        body_y = y + Inches(0.12) + heading_h
        lines = [{'text': it, 'bullet': '▸', 'bullet_color': accent,
                  'size': Pt(14), 'color': LIGHT} for it in items[:3]]
        add_multi_text(slide, x + Inches(0.25), body_y,
                       cell_w - Inches(0.5),
                       cell_h - (body_y - y) - Inches(0.15),
                       lines, default_size=Pt(14), line_spacing=1.3)

    # x-axis label (below the grid)
    add_text(slide, grid_x, top + grid_h + Inches(0.1), grid_w, Inches(0.4),
             "→  " + x_axis, size=SZ_SMALL, color=MUTED,
             align=PP_ALIGN.CENTER, italic=True)
    # y-axis label (to the left, kept horizontal but on one line)
    add_text(slide, MARGIN_X, top + grid_h / 2 - Inches(0.2),
             grid_x - MARGIN_X - Inches(0.1), Inches(0.4),
             y_axis + "  →", size=SZ_SMALL, color=MUTED,
             align=PP_ALIGN.RIGHT, italic=True)
