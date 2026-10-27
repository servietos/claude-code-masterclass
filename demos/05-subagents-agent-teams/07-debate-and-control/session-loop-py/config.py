import json
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")

DEFAULTS = {
    "max_turns": 1,
    "transcript": "transcript.log",
    "prompt": "you> ",
}


def load():
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {
        "max_turns": raw.get("max_turns", DEFAULTS["max_turns"]),
        "transcript": raw.get("transcript", DEFAULTS["transcript"]),
        "prompt": raw.get("prompt", DEFAULTS["prompt"]),
    }
