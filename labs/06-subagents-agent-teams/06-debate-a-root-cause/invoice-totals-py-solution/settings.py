import json
from pathlib import Path


def load_settings(path="config.json"):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "tax_rate": float(raw.get("tax_rate", 0.2)),
        "currency": raw.get("currency", "EUR"),
        "round_each_line": bool(raw.get("round_each_line", True)),
    }
