import re
import sys
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

FONT_DIR = "C:/Windows/Fonts"
FONTS = {
    "Body": "arial.ttf",
    "Body-Bold": "arialbd.ttf",
    "Body-Italic": "ariali.ttf",
    "Body-BoldItalic": "arialbi.ttf",
    "Mono": "consola.ttf",
    "Mono-Bold": "consolab.ttf",
}

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5c5c5c")
ACCENT = colors.HexColor("#b34a1f")
RULE = colors.HexColor("#d4d4d4")
CODE_BG = colors.HexColor("#f4f4f2")
HEAD_BG = colors.HexColor("#efece7")
QUOTE_BG = colors.HexColor("#f7f5f1")


def register_fonts():
    for name, filename in FONTS.items():
        pdfmetrics.registerFont(TTFont(name, f"{FONT_DIR}/{filename}"))
    pdfmetrics.registerFontFamily(
        "Body",
        normal="Body",
        bold="Body-Bold",
        italic="Body-Italic",
        boldItalic="Body-BoldItalic",
    )
    pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-Bold")


def styles():
    base = ParagraphStyle(
        "body",
        fontName="Body",
        fontSize=9.5,
        leading=14.5,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    return {
        "body": base,
        "h1": ParagraphStyle(
            "h1", parent=base, fontName="Body-Bold", fontSize=19, leading=24,
            spaceBefore=16, spaceAfter=8, textColor=ACCENT,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base, fontName="Body-Bold", fontSize=14, leading=19,
            spaceBefore=14, spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base, fontName="Body-Bold", fontSize=11.5, leading=16,
            spaceBefore=11, spaceAfter=4,
        ),
        "h4": ParagraphStyle(
            "h4", parent=base, fontName="Body-Bold", fontSize=10, leading=14,
            spaceBefore=9, spaceAfter=3, textColor=MUTED,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base, leftIndent=11, bulletIndent=2, spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "quote", parent=base, leftIndent=8, rightIndent=6, textColor=MUTED,
            spaceBefore=4, spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "code", parent=base, fontName="Mono", fontSize=7.8, leading=10.4,
            textColor=INK, spaceAfter=0, spaceBefore=0,
        ),
        "th": ParagraphStyle(
            "th", parent=base, fontName="Body-Bold", fontSize=8.6, leading=12,
            spaceAfter=0,
        ),
        "td": ParagraphStyle(
            "td", parent=base, fontSize=8.6, leading=12, spaceAfter=0,
        ),
        "toc": ParagraphStyle(
            "toc", parent=base, fontSize=9, leading=13.5, spaceAfter=2,
            rightIndent=14,
        ),
        "title": ParagraphStyle(
            "title", parent=base, fontName="Body-Bold", fontSize=26, leading=32,
            textColor=ACCENT, spaceAfter=10,
        ),
        "eyebrow": ParagraphStyle(
            "eyebrow", parent=base, fontName="Body-Bold", fontSize=9,
            leading=13, textColor=MUTED, spaceAfter=6,
        ),
        "blurb": ParagraphStyle(
            "blurb", parent=base, fontSize=11, leading=17, textColor=INK,
            spaceAfter=6,
        ),
        "edition": ParagraphStyle(
            "edition", parent=base, fontSize=9, leading=13.5, textColor=MUTED,
            spaceAfter=1,
        ),
    }


INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
ITALIC = re.compile(r"(?<![\*\w])\*([^\*\n]+)\*(?!\*)")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)[^)]*\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)[^)]*\)")


def inline(text):
    text = IMAGE.sub(r"\1", text)
    placeholders = []

    def stash(markup):
        placeholders.append(markup)
        return f"\x00{len(placeholders) - 1}\x00"

    def on_code(m):
        return stash(
            '<font face="Mono" size="8.6" backColor="#f0efec">'
            f"{escape(m.group(1))}</font>"
        )

    text = INLINE_CODE.sub(on_code, text)
    text = escape(text, quote=False)
    text = LINK.sub(
        lambda m: f'<link href="{m.group(2)}" color="#1155aa">{m.group(1)}</link>',
        text,
    )
    text = BOLD.sub(r"<b>\1</b>", text)
    text = ITALIC.sub(r"<i>\1</i>", text)
    text = text.replace("\\", "")
    for i, markup in enumerate(placeholders):
        text = text.replace(f"\x00{i}\x00", markup)
    return text


def wrap_code(line, limit):
    if len(line) <= limit:
        return [line]
    out = []
    while len(line) > limit:
        cut = line.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        out.append(line[:cut])
        line = line[cut:].lstrip()
    out.append(line)
    return out


def code_block(lines, lang, st):
    limit = int(CONTENT_W / pdfmetrics.stringWidth("0", "Mono", 7.8)) - 4
    body = []
    for line in lines:
        body.extend(wrap_code(line.replace("\t", "    "), limit))
    inner = [Preformatted("\n".join(body) or " ", st["code"])]
    if lang and lang not in ("text", ""):
        inner.insert(
            0,
            Paragraph(
                f'<font face="Mono" size="7" color="#8a8a8a">{escape(lang)}</font>',
                st["code"],
            ),
        )
    table = Table([[inner]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return [Spacer(1, 4), table, Spacer(1, 8)]


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


WORD = re.compile(r"[^\s]+")
MARKUP = re.compile(r"[`*\[\]]")


def widest_word(cells, font):
    widest = 0.0
    for cell in cells:
        for word in WORD.findall(MARKUP.sub("", cell)):
            widest = max(widest, pdfmetrics.stringWidth(word, font, 8.6))
    return widest


def widen_narrow_columns(widths, header, body, ncols):
    floors = []
    for i in range(ncols):
        cells = [r[i] for r in body if i < len(r)]
        floor = max(widest_word([header[i]], "Body-Bold"), widest_word(cells, "Body"))
        floors.append(min(floor + 12, CONTENT_W / 3))

    deficit = sum(max(0.0, floors[i] - widths[i]) for i in range(ncols))
    if deficit <= 0:
        return widths

    surplus = [max(0.0, widths[i] - floors[i]) for i in range(ncols)]
    pool = sum(surplus)
    if pool <= 0:
        return widths

    freed = min(deficit, pool)
    for i in range(ncols):
        if surplus[i] > 0:
            widths[i] -= surplus[i] * freed / pool
        else:
            widths[i] += (floors[i] - widths[i]) * freed / deficit
    return widths


def table_block(rows, st):
    header, body = rows[0], rows[1:]
    ncols = max(len(r) for r in rows)
    header += [""] * (ncols - len(header))
    weights = []
    for i in range(ncols):
        longest = max([len(header[i])] + [len(r[i]) for r in body if i < len(r)] + [1])
        weights.append(min(max(longest, 8), 90))
    total = sum(weights)
    widths = [CONTENT_W * w / total for w in weights]
    widths = widen_narrow_columns(widths, header, body, ncols)

    data = [[Paragraph(inline(c), st["th"]) for c in header]]
    for r in body:
        r = r + [""] * (ncols - len(r))
        data.append([Paragraph(inline(c), st["td"]) for c in r])

    table = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(2, len(data), 2):
        style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#fafafa")))
    table.setStyle(TableStyle(style))
    return [Spacer(1, 4), table, Spacer(1, 9)]


def quote_block(lines, st):
    paras = [Paragraph(inline(l), st["quote"]) for l in lines if l.strip()]
    table = Table([[paras]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), QUOTE_BG),
                ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return [Spacer(1, 3), table, Spacer(1, 8)]


HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE = re.compile(r"^\s*```\s*([A-Za-z0-9_+-]*)\s*$")
BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
ORDERED = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
COMMENT = re.compile(r"<!--.*?-->", re.S)
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def front_matter(md):
    match = FRONT_MATTER.match(md)
    if not match:
        return {}, md
    meta = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, md[match.end():]


def cover(meta, st):
    flow = [Spacer(1, 42 * mm)]
    if meta.get("eyebrow"):
        flow.append(Paragraph(inline(meta["eyebrow"]), st["eyebrow"]))
    flow.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT))
    flow.append(Spacer(1, 10))
    flow.append(Paragraph(inline(meta.get("title", "")), st["title"]))
    if meta.get("blurb"):
        flow.append(Spacer(1, 6))
        flow.append(Paragraph(inline(meta["blurb"]), st["blurb"]))
    flow.append(Spacer(1, 26 * mm))
    for line in meta.get("edition", "").split(" | "):
        if line.strip():
            flow.append(Paragraph(inline(line.strip()), st["edition"]))
    flow.append(PageBreak())
    return flow


def contents(st):
    toc = TableOfContents()
    toc.dotsMinLevel = 0
    toc.levelStyles = [st["toc"]]
    return [toc]


def parse(md, st):
    md = COMMENT.sub("", md)
    lines = md.replace("\r\n", "\n").split("\n")
    flow = []
    para = []
    i = 0

    def flush():
        if para:
            flow.append(Paragraph(inline(" ".join(para)), st["body"]))
            para.clear()

    while i < len(lines):
        line = lines[i]

        fence = FENCE.match(line)
        if fence:
            flush()
            lang = fence.group(1)
            i += 1
            buf = []
            while i < len(lines) and not FENCE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1
            flow.extend(code_block(buf, lang, st))
            continue

        if not line.strip():
            flush()
            i += 1
            continue

        if line.strip() == "[TOC]":
            flush()
            flow.extend(contents(st))
            i += 1
            continue

        if HR.match(line):
            flush()
            flow.append(Spacer(1, 5))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
            flow.append(Spacer(1, 7))
            i += 1
            continue

        head = HEADING.match(line)
        if head:
            flush()
            level = min(len(head.group(1)), 4)
            key = f"h{level}"
            title = Paragraph(inline(head.group(2)), st[key])
            if level == 1:
                pos = len(flow)
                if (
                    flow
                    and isinstance(flow[-1], Paragraph)
                    and flow[-1].style.name == "h4"
                ):
                    pos -= 1
                opener = [
                    HRFlowable(width="100%", thickness=1.4, color=ACCENT),
                    Spacer(1, 4),
                ]
                if pos and not isinstance(flow[pos - 1], PageBreak):
                    opener.insert(0, PageBreak())
                flow[pos:pos] = opener
            flow.append(title)
            i += 1
            continue

        if line.lstrip().startswith("|") and "|" in line:
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            rows = [split_row(r) for r in block]
            rows = [
                r for r in rows
                if not all(re.fullmatch(r":?-{2,}:?", c or "-") for c in r)
            ]
            if rows:
                flush()
                flow.extend(table_block(rows, st))
            continue

        if line.lstrip().startswith(">"):
            flush()
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].strip())
                i += 1
            flow.extend(quote_block(buf, st))
            continue

        bullet = BULLET.match(line)
        ordered = ORDERED.match(line)
        if bullet or ordered:
            flush()
            while i < len(lines):
                b = BULLET.match(lines[i])
                o = ORDERED.match(lines[i])
                if not (b or o):
                    break
                indent = len((b or o).group(1))
                mark = "\u2022" if b else f"{o.group(2)}."
                text = b.group(2) if b else o.group(3)
                i += 1
                while (
                    i < len(lines)
                    and lines[i].strip()
                    and not BULLET.match(lines[i])
                    and not ORDERED.match(lines[i])
                    and lines[i].startswith(" ")
                ):
                    text += " " + lines[i].strip()
                    i += 1
                style = ParagraphStyle(
                    "b", parent=st["bullet"], leftIndent=11 + indent * 6,
                    bulletIndent=2 + indent * 6,
                )
                flow.append(Paragraph(inline(text), style, bulletText=mark))
            flow.append(Spacer(1, 5))
            continue

        para.append(line.strip())
        i += 1

    flush()
    return flow


class Handout(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "h1":
            self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))


def build(src, dst, fallback_title):
    st = styles()
    meta, md = front_matter(open(src, encoding="utf-8").read())
    title = meta.get("title", fallback_title)
    footer_text = meta.get("footer", title)

    def decorate(canvas, doc):
        if doc.page == 1 and meta:
            return
        canvas.saveState()
        canvas.setFont("Body", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, 12 * mm, footer_text)
        canvas.drawRightString(PAGE_W - MARGIN, 12 * mm, f"Page {doc.page}")
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, 15 * mm, PAGE_W - MARGIN, 15 * mm)
        canvas.restoreState()

    doc = Handout(
        dst,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN + 4 * mm,
        title=title,
        author="Claude Code Masterclass",
    )
    frame = Frame(
        MARGIN, MARGIN + 4 * mm, CONTENT_W,
        PAGE_H - MARGIN - (MARGIN + 4 * mm), id="main",
    )
    doc.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=decorate)])
    doc.multiBuild((cover(meta, st) if meta else []) + parse(md, st))


if __name__ == "__main__":
    register_fonts()
    build(sys.argv[1], sys.argv[2], sys.argv[3])
