"""Fetch Lucide SVG icons, recolor them, convert to PNG.

Lucide icons (https://lucide.dev) are ISC-licensed stroke SVGs. We download
them, set the stroke color via XML attribute, and rasterize via cairosvg.
"""

import os
import urllib.request
import re
import cairosvg

LUCIDE_BASE = "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons"

ICONS_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "images", "icons"))
os.makedirs(ICONS_DIR, exist_ok=True)

# Color palette
CORAL = "#E8734A"
AMBER = "#F5A623"
WHITE = "#FAFAFA"
LIGHT = "#E0E0E8"

# (slug, lucide-name, hex-color, output-size-px)
ICON_SET = [
    # Module divider glyphs
    ("module-01", "rocket", AMBER, 512),
    ("module-02", "settings-2", AMBER, 512),
    ("module-03", "plug-zap", AMBER, 512),
    ("module-04", "wrench", AMBER, 512),
    ("module-05", "clipboard-list", AMBER, 512),
    ("module-06", "trending-up", AMBER, 512),
    ("module-07", "users", AMBER, 512),
    ("module-08", "network", AMBER, 512),
    ("module-09", "terminal", AMBER, 512),
    ("module-10", "cloud-cog", AMBER, 512),
    ("module-11", "shield-check", AMBER, 512),
    ("module-12", "puzzle", AMBER, 512),
    ("module-13", "square-code", AMBER, 512),
    ("module-14", "cloud-upload", AMBER, 512),

    # Sub-agent topology
    ("agent-backend", "server", WHITE, 256),
    ("agent-frontend", "monitor", WHITE, 256),
    ("agent-testing", "flask-conical", WHITE, 256),
    ("agent-docs", "book-open", WHITE, 256),

    # Welcome cards
    ("welcome-about", "compass", AMBER, 256),
    ("welcome-need", "laptop", AMBER, 256),

    # Takeaway check icons
    ("takeaway-check", "circle-check", WHITE, 128),

    # Settings hierarchy tier icons
    ("tier-enterprise", "building-2", WHITE, 256),
    ("tier-user", "user", LIGHT, 256),
    ("tier-project", "folder-git-2", LIGHT, 256),
    ("tier-local", "folder", LIGHT, 256),
    ("tier-session", "square-terminal", LIGHT, 256),

    # Permission layer icons (network/bash/files)
    ("perm-network", "globe", WHITE, 256),
    ("perm-bash", "terminal", WHITE, 256),
    ("perm-files", "file-text", WHITE, 256),
]


def fetch_svg(name: str) -> str:
    url = f"{LUCIDE_BASE}/{name}.svg"
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.read().decode("utf-8")


def colorize(svg: str, color: str, stroke_width: float = 1.8) -> str:
    """Inject explicit stroke colour + width onto every line/path."""
    svg = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', svg)
    svg = re.sub(r'stroke-width="[^"]*"',
                 f'stroke-width="{stroke_width}"', svg)
    if 'stroke="' not in svg:
        svg = svg.replace('<svg', f'<svg stroke="{color}"', 1)
    return svg


def main():
    for slug, name, color, size in ICON_SET:
        out_path = os.path.join(ICONS_DIR, f"{slug}.png")
        if os.path.exists(out_path):
            print(f"  skip {slug}")
            continue
        try:
            svg = fetch_svg(name)
        except Exception as e:
            print(f"  ! fetch failed: {slug}/{name} — {e}")
            continue
        svg = colorize(svg, color)
        try:
            png = cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                                   output_width=size, output_height=size)
        except Exception as e:
            print(f"  ! convert failed: {slug} — {e}")
            continue
        with open(out_path, "wb") as f:
            f.write(png)
        print(f"  ok   {slug} ({size}px)")


if __name__ == "__main__":
    main()
