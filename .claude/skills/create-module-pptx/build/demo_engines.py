"""Smoke-test the d2 + chart diagram_types end-to-end through render_deck."""
import build_pptx

slides = [
    {"type": "diagram", "diagram_type": "d2",
     "title": "How a Turn Flows", "subtitle": "the agentic loop, as a graph",
     "d2": """
prompt.class: svc
prompt.label: "Your prompt"
ctx.class: svc
ctx.label: "Context · CLAUDE.md, files"
model.class: hl
model.label: "Claude"
tools.class: svc
tools.label: "Tools · read / edit / bash"
verify.class: hl
verify.label: "Verify"
prompt -> model
ctx -> model
model -> tools
tools -> model
model -> verify
"""},
    {"type": "diagram", "diagram_type": "chart",
     "title": "Capability — baseline vs Claude Code",
     "chart": {"kind": "radar",
               "labels": ["Speed", "Quality", "Autonomy", "Safety", "Reuse"],
               "series": [{"name": "Baseline", "values": [4, 5, 3, 6, 4]},
                          {"name": "With Claude Code", "values": [9, 8, 9, 8, 9]}]}},
    {"type": "diagram", "diagram_type": "chart",
     "title": "Labs per chapter", "subtitle": "hands-on throughout",
     "chart": {"kind": "bar", "ylabel": "labs",
               "labels": ["Ch1", "Ch2", "Ch3", "Ch4", "Ch5"],
               "series": [{"name": "Labs", "values": [2, 2, 4, 3, 5]}]}},
]
n = build_pptx.render_deck(slides, "/tmp/engines_demo.pptx")
print(f"built /tmp/engines_demo.pptx ({n} slides)")
