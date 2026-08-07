"""Deep Sea-themed diagram engines for the `diagram` slide type.

- d2     : structural diagrams (D2 binary, rendered natively to PNG)
- chart  : data charts (Matplotlib with a Deep Sea stylesheet)

Both render to ../images/generated/<hash>.png and are embedded by
layouts.render_diagram. Authors write the diagram/data as text in the YAML.
"""

import os
import math
import hashlib
import subprocess

import theme

GENERATED_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'images', 'generated'))


def _hex(c):
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


GROUND = _hex(theme.GROUND)
CARD = _hex(theme.CARD)
CARD_HI = _hex(theme.CARD_HI)
PRIMARY = _hex(theme.PRIMARY)
ACCENT = _hex(theme.ACCENT)
POP = _hex(theme.POP)
TEXT = _hex(theme.TEXT)
MUTED = _hex(theme.TEXT_MUTED)
ON_PRIMARY = _hex(theme.ON_PRIMARY)

# Injected into every d2 source so authors just use {class: svc|hl} on nodes.
D2_PREAMBLE = f"""style.fill: "{GROUND}"
classes: {{
  svc: {{ style: {{ fill: "{CARD}"; stroke: "#0a4853"; stroke-width: 2; font-color: "{TEXT}"; border-radius: 10 }} }}
  hl:  {{ style: {{ fill: "{PRIMARY}"; stroke: "{PRIMARY}"; font-color: "{ON_PRIMARY}"; border-radius: 10 }} }}
  link:{{ style: {{ stroke: "{ACCENT}"; stroke-width: 2 }} }}
}}
"""


def cache_path(kind, source):
    os.makedirs(GENERATED_DIR, exist_ok=True)
    h = hashlib.md5((kind + repr(source)).encode()).hexdigest()[:12]
    return os.path.join(GENERATED_DIR, f"{kind}_{h}.png")


def render_d2(source, out_path):
    src = D2_PREAMBLE + "\n" + source
    d2file = out_path.replace('.png', '.d2')
    with open(d2file, 'w') as f:
        f.write(src)
    subprocess.run(["d2", "--scale", "2", d2file, out_path],
                   check=True, capture_output=True, timeout=120)
    return out_path


_STYLE_SET = False


def _ensure_style():
    global _STYLE_SET
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt
    if _STYLE_SET:
        return plt
    for fp in ("Manrope-VF.ttf", "Inter-VF.ttf"):
        p = os.path.expanduser(f"~/Library/Fonts/{fp}")
        if os.path.exists(p):
            fm.fontManager.addfont(p)
    plt.rcParams.update({
        "figure.facecolor": GROUND, "axes.facecolor": GROUND,
        "savefig.facecolor": GROUND, "text.color": TEXT,
        "axes.labelcolor": TEXT, "axes.edgecolor": "#1e3c46",
        "xtick.color": TEXT, "ytick.color": MUTED, "font.family": "Manrope",
        "axes.grid": True, "grid.color": "#15323a", "axes.spines.top": False,
        "axes.spines.right": False,
    })
    _STYLE_SET = True
    return plt


_CYCLE = [PRIMARY, ACCENT, POP, "#6fe0a0"]


def render_chart(spec, out_path):
    plt = _ensure_style()
    kind = spec.get("kind", "bar")
    labels = spec.get("labels", [])
    series = spec.get("series", [])
    fig = plt.figure(figsize=(10.5, 5.0))

    if kind == "radar":
        ax = plt.subplot(111, polar=True)
        ax.set_facecolor(GROUND)
        n = len(labels)
        ang = [i / n * 2 * math.pi for i in range(n)] + [0]
        ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, fontsize=13)
        ax.set_yticklabels([]); ax.set_ylim(0, spec.get("max", 10))
        ax.spines["polar"].set_color("#1e3c46")
        for i, s in enumerate(series):
            v = s["values"] + s["values"][:1]
            col = _CYCLE[i % len(_CYCLE)]
            ax.plot(ang, v, color=col, linewidth=2, label=s.get("name"))
            ax.fill(ang, v, color=col, alpha=0.18)
        if any(s.get("name") for s in series):
            ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1),
                      frameon=False, labelcolor=TEXT)
    else:
        ax = plt.subplot(111)
        ax.set_facecolor(GROUND)
        x = range(len(labels))
        nfields = max(len(series), 1)
        for i, s in enumerate(series):
            col = _CYCLE[i % len(_CYCLE)]
            if kind == "line":
                ax.plot(labels, s["values"], color=col, linewidth=2.5,
                        marker="o", label=s.get("name"))
            else:  # bar (grouped)
                w = 0.8 / nfields
                off = [xx + (i - (nfields - 1) / 2) * w for xx in x]
                ax.bar(off, s["values"], width=w, color=col, label=s.get("name"))
        if kind != "line":
            ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=12)
        if spec.get("ylabel"):
            ax.set_ylabel(spec["ylabel"])
        if any(s.get("name") for s in series):
            ax.legend(frameon=False, labelcolor=TEXT, fontsize=11)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path
