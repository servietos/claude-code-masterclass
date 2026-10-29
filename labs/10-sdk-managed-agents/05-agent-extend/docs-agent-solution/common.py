import json
import sys
import time
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
sys.stdout.reconfigure(encoding="utf-8")

client = Anthropic()
suffix = uuid4().hex[:8]
here = Path(__file__).parent
runs_file = here / "runs.json"


def text_of(blocks):
    return " ".join(block.text for block in blocks if block.type == "text")


def send_task(session_id, text):
    client.beta.sessions.events.send(
        session_id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
    )


def record_run(session_id, environment_id):
    runs = json.loads(runs_file.read_text()) if runs_file.exists() else []
    runs.append({"session": session_id, "environment": environment_id})
    runs_file.write_text(json.dumps(runs, indent=2))


def watch(session_id, on_event, stop_on_requires_action=False):
    seen = 0
    while True:
        current = client.beta.sessions.retrieve(session_id)
        log = list(client.beta.sessions.events.list(session_id, order="asc"))
        for event in log[seen:]:
            on_event(event)
        seen = len(log)
        idle = [event for event in log if event.type == "session.status_idle"]
        if current.status == "terminated":
            return log
        if idle:
            reason = idle[-1].stop_reason.type
            if reason != "requires_action" or stop_on_requires_action:
                return log
        time.sleep(3)
