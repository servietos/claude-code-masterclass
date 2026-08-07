"""Fast Lane masterclass theme — Deep Sea colorway.

Teal-black ground, teal signature, orange Fast Lane accent, no-line tonal
cards. Old constant names are retained (the whole generator reads them) and
remapped to Deep Sea tokens; new semantic tokens are added for the port.
"""

from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor


def _c(h):
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# --- Deep Sea tokens (semantic) ---
GROUND = _c("00161b")
GROUND2 = _c("001f25")
CARD = _c("00242a")
CARD_HI = _c("003b44")
PRIMARY = _c("78d3e9")
PRIMARY_BRIGHT = _c("a9edff")
ACCENT = _c("ff9456")
ACCENT_SOFT = _c("ffb68d")
POP = _c("cdbdff")
TEXT = _c("e8f3f1")
TEXT_MUTED = _c("7fa0a6")
ON_PRIMARY = _c("042830")  # dark text for use ON teal fills (high contrast)

# --- legacy names remapped onto Deep Sea (keeps layouts/diagrams working) ---
CORAL = PRIMARY          # primary accent: title rules, bullets, frames
AMBER = ACCENT           # secondary accent: subtitles, highlights
GOLD = ACCENT_SOFT
DARK = GROUND
DARKER = _c("001014")
NAVY_GRAD = CARD_HI      # gradient partner
LIGHT = TEXT
MUTED = TEXT_MUTED
WHITE = _c("ffffff")
GREEN = _c("6fe0a0")
RED = _c("ff8a8a")
BAD_BG = _c("2a1518")
GOOD_BG = _c("0e2a20")
PANEL_BG = CARD
PANEL_HI = CARD_HI
CODE_BG = _c("00121a")


FONT_HEADING = "Manrope"
FONT_BODY = "Inter"
FONT_MONO = "Menlo"


SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN_X = Inches(0.6)
MARGIN_TOP = Inches(0.55)
MARGIN_BOTTOM = Inches(0.5)
CONTENT_W = SLIDE_W - MARGIN_X * 2

FOOTER_BAND = Inches(0.42)
CONTENT_SAFE_BOTTOM = SLIDE_H - FOOTER_BAND - Inches(0.13)

TITLE_TOP = Inches(0.45)
TITLE_H = Inches(0.7)
SUBTITLE_TOP = Inches(1.15)
SUBTITLE_H = Inches(0.45)
BODY_TOP = Inches(1.55)
BODY_H = Inches(5.4)


SZ_HERO_TITLE = Pt(72)
SZ_HERO_SUBTITLE = Pt(28)
SZ_HERO_TAGLINE = Pt(18)
SZ_TITLE = Pt(32)
SZ_SUBTITLE = Pt(20)
SZ_H3 = Pt(20)
SZ_BODY = Pt(18)
SZ_SMALL = Pt(14)
SZ_TINY = Pt(11)
SZ_CARD_NUMBER = Pt(40)
SZ_CARD_LABEL = Pt(12)
SZ_WATERMARK = Pt(10)
SZ_CODE = Pt(13)
