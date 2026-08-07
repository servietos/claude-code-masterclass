"""Shared visual system for the varied redesign.

Provides per-chapter accent rotation, an editorial header, subtle background
geometry to fill the lower frame, and a native-chart helper for real graphs.
Renderers read the chapter from the slide dict (build_pptx propagates it), so
no global state is needed.
"""

from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.oxml.ns import qn

from theme import (
    PRIMARY, ACCENT, POP, PRIMARY_BRIGHT, GREEN, RED, CARD, CARD_HI, GROUND2,
    TEXT, TEXT_MUTED, WHITE, ON_PRIMARY, MUTED, LIGHT,
    FONT_HEADING, FONT_BODY,
    SLIDE_W, SLIDE_H, MARGIN_X, CONTENT_W, TITLE_TOP, BODY_TOP,
    CONTENT_SAFE_BOTTOM, SZ_TITLE, SZ_SUBTITLE,
)
from helpers import add_rect, add_text, set_solid_fill, set_line


# Concept-coded color system. Each color means one thing across the whole
# deck, so the palette teaches instead of merely decorating:
#   structure/harness -> teal   · action/CLI -> orange
#   agent/AI reasoning -> violet · safe/verify -> green · danger -> red
ROLE_COLORS = {
    'structure': PRIMARY,
    'action': ACCENT,
    'agent': POP,
    'safe': GREEN,
    'danger': RED,
}

# Default role by slide type when a slide doesn't declare `role:` explicitly.
# Anything not listed falls back to 'structure' (teal).
_DEFAULT_ROLE_BY_TYPE = {
    'terminal': 'action',
    'code': 'action',
    'lab': 'action',
    'takeaways': 'safe',
}


def accent_for(data):
    """Concept color for a slide. Honors an explicit `role:`, else defaults by
    slide type. 'agent' (violet) is opt-in via role so it lands only on real
    agent/AI-reasoning content, not anything that merely says 'agent'."""
    role = data.get('role')
    if role not in ROLE_COLORS:
        role = _DEFAULT_ROLE_BY_TYPE.get(data.get('type'), 'structure')
    return ROLE_COLORS[role]


def content_band():
    """(top, height) of the usable area below the header, above the footer."""
    top = BODY_TOP + Inches(0.35)
    return top, CONTENT_SAFE_BOTTOM - top


def optical_top(band_top, band_h, block_h, factor=0.43):
    """Top offset that sits a block at the optical center of the band.

    True center (0.5) reads slightly low for a single element under a header;
    biasing to ~0.43 lifts it so the composition feels settled, not floating."""
    off = (band_h - block_h) * factor
    if off < 0:
        off = 0
    return band_top + off


def add_bg_accent(slide, accent, data=None):
    """No-op. A large ghost numeral was tried as a void-filler but collided with
    headlines/body text on dense slides; confident whitespace is the more
    premium choice, so this intentionally draws nothing. Kept for call-site
    compatibility."""
    return


def window_chrome(slide, x, y, w, h, *, title='', accent=PRIMARY):
    """Mac-style window: rounded body + title bar with three traffic dots.

    Used by the terminal slide type so command-line content reads like the real
    tool rather than another bullet card.
    """
    body = add_rect(slide, x, y, w, h, fill=GROUND2, line=None, corner=0.025)
    bar_h = Inches(0.42)
    bar = add_rect(slide, x, y, w, bar_h, fill=CARD_HI, line=None, corner=0.025)
    dots = [(0xff, 0x5f, 0x56), (0xff, 0xbd, 0x2e), (0x27, 0xc9, 0x3f)]
    for i, rgb in enumerate(dots):
        d = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                   int(x + Inches(0.25) + Inches(0.32) * i),
                                   int(y + bar_h / 2 - Inches(0.075)),
                                   Inches(0.15), Inches(0.15))
        d.fill.solid(); d.fill.fore_color.rgb = RGBColor(*rgb)
        set_line(d, None); d.shadow.inherit = False
    if title:
        add_text(slide, x + Inches(1.4), y, w - Inches(2.8), bar_h,
                 title, size=Pt(12), color=TEXT_MUTED, font=FONT_BODY,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return y + bar_h


def add_header(slide, data, title, subtitle=None):
    """Editorial header: a tall accent tick at the left edge of the title, a
    small chapter kicker above it, title indented past the tick. Replaces the
    repeated centered-underline so slides stop looking stamped.
    """
    accent = accent_for(data)
    tick_x = MARGIN_X
    text_x = MARGIN_X + Inches(0.32)

    kicker = data.get('chapter_label')
    mod = data.get('module')
    if kicker:
        label = f"MODULE {mod:02d} · {kicker}".upper() if mod else kicker.upper()
        add_text(slide, text_x, Inches(0.34), CONTENT_W, Inches(0.3),
                 label, size=Pt(12), color=accent, bold=True,
                 font=FONT_HEADING)

    tick = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  tick_x, Inches(0.66),
                                  Inches(0.14), Inches(0.62))
    set_solid_fill(tick, accent)
    set_line(tick, None)
    tick.shadow.inherit = False
    try:
        tick.adjustments[0] = 0.5
    except Exception:
        pass

    t_sz = SZ_TITLE
    if len(title) > 52:
        t_sz = Pt(25)
    elif len(title) > 40:
        t_sz = Pt(28)
    add_text(slide, text_x, Inches(0.62), CONTENT_W - Inches(0.4), Inches(0.8),
             title, size=t_sz, color=WHITE, bold=True, font=FONT_HEADING)
    if subtitle:
        add_text(slide, text_x, Inches(1.4), CONTENT_W - Inches(0.4),
                 Inches(0.4), subtitle, size=SZ_SUBTITLE, color=accent,
                 italic=True)
    return accent


def _style_chart_font(chart):
    chart.font.name = FONT_BODY
    chart.font.size = Pt(12)
    chart.font.color.rgb = TEXT


def _hex(c):
    return f'{c[0]:02X}{c[1]:02X}{c[2]:02X}'


def add_bar_chart(slide, x, y, w, h, categories, values, accent,
                  *, value_suffix=''):
    cd = CategoryChartData()
    cd.categories = categories
    cd.add_series('series', values)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                                x, y, w, h, cd)
    chart = gf.chart
    chart.has_title = False
    chart.has_legend = False
    _style_chart_font(chart)
    plot = chart.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = f'0"{value_suffix}"' if value_suffix else '0'
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(13)
    dl.font.bold = True
    dl.font.color.rgb = WHITE
    series = plot.series[0]
    tints = [accent, CARD_HI, accent, CARD_HI, accent, CARD_HI]
    for i, pt in enumerate(series.points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = accent if i % 2 == 0 else CARD_HI
        pt.format.line.fill.background()
    cat_ax = chart.category_axis
    cat_ax.has_major_gridlines = False
    cat_ax.tick_labels.font.size = Pt(12)
    cat_ax.tick_labels.font.color.rgb = TEXT
    cat_ax.format.line.color.rgb = TEXT_MUTED
    val_ax = chart.value_axis
    val_ax.has_major_gridlines = False
    val_ax.visible = False
    return gf


def add_donut_chart(slide, x, y, w, h, labels, values, accent):
    cd = CategoryChartData()
    cd.categories = labels
    cd.add_series('series', values)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, x, y, w, h, cd)
    chart = gf.chart
    chart.has_title = False
    _style_chart_font(chart)
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.RIGHT
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(12)
    chart.legend.font.color.rgb = TEXT
    plot = chart.plots[0]
    palette = [accent, CARD_HI, POP, PRIMARY_BRIGHT, ACCENT, GREEN]
    series = plot.series[0]
    for i, pt in enumerate(series.points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = palette[i % len(palette)]
        pt.format.line.color.rgb = GROUND2
        pt.format.line.width = Pt(2)
    return gf


def add_progress_rows(slide, x, y, w, rows, accent, *, row_h=None, gap=None):
    """Horizontal progress/stat bars: label + track + filled portion + value.

    rows: list of {label, pct (0-100), value?}.  A lightweight 'graph' that
    fits qualitative comparisons where a full chart would be overkill.
    """
    row_h = row_h or Inches(0.52)
    gap = gap or Inches(0.34)
    label_w = Inches(3.2)
    track_x = x + label_w
    track_w = w - label_w - Inches(0.9)
    for i, r in enumerate(rows):
        ry = y + (row_h + gap) * i
        add_text(slide, x, ry, label_w - Inches(0.15), row_h,
                 r.get('label', ''), size=Pt(15), color=LIGHT,
                 anchor=MSO_ANCHOR.MIDDLE, font=FONT_BODY)
        bar_h = Inches(0.26)
        bar_y = ry + (row_h - bar_h) / 2
        add_rect(slide, track_x, bar_y, track_w, bar_h, fill=CARD_HI,
                 line=None, corner=0.5)
        pct = max(0, min(100, r.get('pct', 0)))
        fill_w = Emu(int(track_w * pct / 100.0))
        if fill_w > 0:
            add_rect(slide, track_x, bar_y, fill_w, bar_h, fill=accent,
                     line=None, corner=0.5)
        add_text(slide, track_x + track_w + Inches(0.1), ry,
                 Inches(0.8), row_h,
                 r.get('value', f"{pct}%"), size=Pt(14), color=accent,
                 bold=True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT,
                 font=FONT_HEADING)
