"""Low-level helpers for shape construction on a slide."""

from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

from theme import (
    DARK, DARKER, CORAL, AMBER, GOLD, LIGHT, MUTED, WHITE, NAVY_GRAD,
    FONT_HEADING, FONT_BODY, FONT_MONO,
    SLIDE_W, SLIDE_H, MARGIN_X, TITLE_TOP, TITLE_H, BODY_TOP, BODY_H, CONTENT_W,
    SZ_TITLE, SZ_SUBTITLE, SZ_BODY, SZ_SMALL, SZ_TINY, SZ_WATERMARK,
)


def _i(v):
    """Coerce length-like values to integer EMU."""
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return v


def set_solid_fill(shape, color: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def set_no_fill(shape):
    shape.fill.background()


def set_line(shape, color: RGBColor | None, width_pt: float = 1.0):
    if color is None:
        shape.line.fill.background()
        return
    shape.line.color.rgb = color
    shape.line.width = Pt(width_pt)


def set_slide_background(slide, color: RGBColor):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def set_slide_background_gradient(slide, color_a: RGBColor, color_b: RGBColor):
    # cSld is the parent of p:bg and p:spTree. Walk up from spTree to cSld.
    sp_tree = slide.shapes._spTree
    cSld = sp_tree.getparent()
    # remove any existing p:bg at this level
    for existing in cSld.findall(qn('p:bg')):
        cSld.remove(existing)
    # p:bg must come BEFORE p:spTree per OOXML schema
    bg_el = etree.SubElement(cSld, qn('p:bg'))
    cSld.remove(bg_el)
    cSld.insert(0, bg_el)
    bg_pr = etree.SubElement(bg_el, qn('p:bgPr'))
    grad = etree.SubElement(bg_pr, qn('a:gradFill'))
    grad.set('rotWithShape', '1')
    gs_lst = etree.SubElement(grad, qn('a:gsLst'))

    def add_stop(pos, rgb):
        gs = etree.SubElement(gs_lst, qn('a:gs'))
        gs.set('pos', str(pos))
        srgb = etree.SubElement(gs, qn('a:srgbClr'))
        srgb.set('val', f'{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}')

    add_stop(0, color_a)
    add_stop(100000, color_b)
    lin = etree.SubElement(grad, qn('a:lin'))
    lin.set('ang', '2700000')
    lin.set('scaled', '1')
    # effectLst is required to close p:bgPr cleanly
    etree.SubElement(bg_pr, qn('a:effectLst'))


def add_rect(slide, x, y, w, h, fill: RGBColor | None = DARKER,
             line: RGBColor | None = None, rounded: bool = True, corner: float = 0.05):
    shp_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shp_type, _i(x), _i(y), _i(w), _i(h))
    if rounded:
        try:
            shape.adjustments[0] = corner
        except Exception:
            pass
    if fill is None:
        set_no_fill(shape)
    else:
        set_solid_fill(shape, fill)
    if line is None:
        shape.line.fill.background()
    else:
        set_line(shape, line, 1.25)
    shape.shadow.inherit = False
    return shape


def add_text(slide, x, y, w, h, text, *, size=SZ_BODY, color=LIGHT,
             font=FONT_BODY, bold=False, italic=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    tb = slide.shapes.add_textbox(_i(x), _i(y), _i(w), _i(h))
    tb.text_frame.word_wrap = True
    tb.text_frame.margin_left = Inches(0.05)
    tb.text_frame.margin_right = Inches(0.05)
    tb.text_frame.margin_top = Inches(0.02)
    tb.text_frame.margin_bottom = Inches(0.02)
    tb.text_frame.vertical_anchor = anchor
    p = tb.text_frame.paragraphs[0]
    p.alignment = align
    if line_spacing:
        p.line_spacing = line_spacing
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = size
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    return tb


def add_multi_text(slide, x, y, w, h, lines, *, default_size=SZ_BODY,
                   default_color=LIGHT, font=FONT_BODY, align=PP_ALIGN.LEFT,
                   anchor=MSO_ANCHOR.TOP, line_spacing=1.15,
                   shrink_to_fit=False):
    """lines: list of dicts {text, size?, color?, bold?, italic?, bullet?}

    shrink_to_fit=True replaces spAutoFit with normAutofit so PowerPoint
    auto-scales font size down if content would overflow the fixed box.
    """
    tb = slide.shapes.add_textbox(_i(x), _i(y), _i(w), _i(h))
    tf = tb.text_frame
    tf.word_wrap = True
    if shrink_to_fit:
        bodyPr = tf._txBody.find(qn('a:bodyPr'))
        if bodyPr is not None:
            for spAutoFit in bodyPr.findall(qn('a:spAutoFit')):
                bodyPr.remove(spAutoFit)
            for normAutofit in bodyPr.findall(qn('a:normAutofit')):
                bodyPr.remove(normAutofit)
            etree.SubElement(bodyPr, qn('a:normAutofit'))
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    tf.vertical_anchor = anchor
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        prefix = line.get('bullet')
        if prefix:
            # Hanging indent, so a wrapped item aligns under its own text
            # instead of reading as a second, bullet-less item.
            hang = int(Inches(0.26))
            pPr = p._p.get_or_add_pPr()
            pPr.set('marL', str(hang))
            pPr.set('indent', str(-hang))
            r0 = p.add_run()
            r0.text = prefix + " "
            r0.font.name = font
            r0.font.size = line.get('size', default_size)
            r0.font.color.rgb = line.get('bullet_color', CORAL)
            r0.font.bold = True
        run = p.add_run()
        run.text = line['text']
        run.font.name = line.get('font', font)
        run.font.size = line.get('size', default_size)
        run.font.color.rgb = line.get('color', default_color)
        run.font.bold = line.get('bold', False)
        run.font.italic = line.get('italic', False)
    return tb


def add_title(slide, title, subtitle=None):
    add_text(slide, MARGIN_X, TITLE_TOP, CONTENT_W, TITLE_H,
             title, size=SZ_TITLE, color=WHITE, bold=True, font=FONT_HEADING)
    # Coral accent line under title
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    MARGIN_X, TITLE_TOP + Inches(0.78),
                                    Inches(1.2), Inches(0.05))
    set_solid_fill(accent, CORAL)
    set_line(accent, None)
    if subtitle:
        add_text(slide, MARGIN_X, TITLE_TOP + Inches(0.85),
                 CONTENT_W, Inches(0.4),
                 subtitle, size=SZ_SUBTITLE, color=AMBER, italic=True)


def add_watermark(slide, page_num=None, total=None):
    add_text(slide, SLIDE_W - Inches(3.5), SLIDE_H - Inches(0.42),
             Inches(3.3), Inches(0.3),
             "Fast Lane · Claude Code Masterclass",
             size=SZ_WATERMARK, color=CORAL, align=PP_ALIGN.RIGHT)
    if page_num is not None and total is not None:
        add_text(slide, MARGIN_X, SLIDE_H - Inches(0.42),
                 Inches(1.0), Inches(0.3),
                 f"{page_num} / {total}",
                 size=SZ_WATERMARK, color=MUTED)


def add_arrow(slide, x1, y1, x2, y2, color=AMBER, width_pt=1.75):
    conn = slide.shapes.add_connector(2, _i(x1), _i(y1), _i(x2), _i(y2))  # 2 = straight
    line = conn.line
    line.color.rgb = color
    line.width = Pt(width_pt)
    ln = line._get_or_add_ln()
    tail = ln.find(qn('a:tailEnd'))
    if tail is None:
        tail = etree.SubElement(ln, qn('a:tailEnd'))
    tail.set('type', 'triangle')
    tail.set('w', 'med')
    tail.set('h', 'med')
    return conn


def truncate(text: str, max_len: int) -> str:
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"
