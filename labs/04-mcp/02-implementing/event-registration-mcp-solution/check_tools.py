# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
EXPECTED_TOOLS = {
    "list_events",
    "create_event",
    "check_availability",
    "register_attendee",
    "list_registrations",
    "cancel_registration",
    "get_event_summary",
}

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label} {detail}")
    if not condition:
        failures.append(label)


class Client:
    def __init__(self):
        self.proc = subprocess.Popen(
            ["uv", "run", str(HERE / "server.py"), "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self.next_id = 0

    def send(self, method, params=None, notify=False):
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        if not notify:
            self.next_id += 1
            message["id"] = self.next_id
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("server closed stdout")
            response = json.loads(line)
            if response.get("id") == message["id"]:
                return response

    def call_list(self, name, arguments):
        response = self.send("tools/call", {"name": name, "arguments": arguments})
        return [json.loads(block["text"]) for block in response["result"]["content"]]

    def call_tool(self, name, arguments):
        blocks = self.call_list(name, arguments)
        return blocks[0] if blocks else {}

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=30)


client = Client()

init = client.send(
    "initialize",
    {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "lab-check", "version": "1.0"},
    },
)
check("initialize handshake", init["result"]["serverInfo"]["name"] == "EventTrack", init["result"]["serverInfo"])
client.send("notifications/initialized", {}, notify=True)

tools = {t["name"] for t in client.send("tools/list")["result"]["tools"]}
check("tools/list returns exactly seven expected tools", tools == EXPECTED_TOOLS, sorted(tools))

events = client.call_list("list_events", {})
check("list_events returns five events", len(events) == 5, [e["title"] for e in events])
workshop = next(e for e in events if e["title"] == "Workshop: Building MCP Servers in Python")
before = workshop["seats_remaining"]
check("workshop seats_remaining is capacity minus bookings", before == workshop["capacity"] - workshop["registered_count"], before)

registration = client.call_tool(
    "register_attendee",
    {"event_id": workshop["id"], "name": "Alex Rivera", "email": "alex.rivera@example.com"},
)
check("register_attendee succeeds", "error" not in registration, registration)
check("registration carries a UTC timestamp", registration.get("registered_at", "").endswith("+00:00"), registration.get("registered_at"))

duplicate = client.call_tool(
    "register_attendee",
    {"event_id": workshop["id"], "name": "Alex Rivera", "email": "alex.rivera@example.com"},
)
check("duplicate registration returns 'Already registered'", duplicate.get("error") == "Already registered", duplicate)

after = client.call_tool("check_availability", {"event_id": workshop["id"]})
check("check_availability shows one fewer seat", after["seats_remaining"] == before - 1, after["seats_remaining"])

registrations = client.call_list("list_registrations", {"event_id": workshop["id"]})
check(
    "list_registrations joins event_title",
    all(r["event_title"] == workshop["title"] for r in registrations) and len(registrations) == 3,
    len(registrations),
)
check("list_registrations without filter returns all rows", len(client.call_list("list_registrations", {})) == 7)

cancelled = client.call_tool(
    "cancel_registration", {"event_id": workshop["id"], "email": "alex.rivera@example.com"}
)
check("cancel_registration succeeds", "error" not in cancelled, cancelled)
restored = client.call_tool("check_availability", {"event_id": workshop["id"]})
check("seat restored after cancellation", restored["seats_remaining"] == before, restored["seats_remaining"])
check(
    "cancelling again returns 'Registration not found'",
    client.call_tool("cancel_registration", {"event_id": workshop["id"], "email": "alex.rivera@example.com"}).get("error")
    == "Registration not found",
)

lab = next(e for e in events if e["title"] == "Hands-On Lab: FastAPI + Claude Integration")
step8 = [
    ("Jordan Blake", "jordan.blake@example.com"),
    ("Sam Nguyen", "sam.nguyen@example.com"),
    ("Priya Mehta", "priya.mehta@example.com"),
    ("Luca Ferrari", "luca.ferrari@example.com"),
    ("Yuki Tanaka", "yuki.tanaka@example.com"),
]
results = [client.call_tool("register_attendee", {"event_id": lab["id"], "name": n, "email": m}) for n, m in step8]
check("Step 8: all five attendees register successfully", all("error" not in r for r in results), [r.get("error") for r in results])

summary = client.call_tool("get_event_summary", {"event_id": lab["id"]})
check(
    "get_event_summary reports the five attendees",
    summary["registered_count"] == 5 and summary["seats_remaining"] == 15 and len(summary["attendees"]) == 5,
    (summary["registered_count"], summary["seats_remaining"]),
)

created = client.call_tool(
    "create_event",
    {
        "title": "Lightning Talks",
        "description": "Five-minute talks",
        "date": "2026-09-17",
        "venue": "Room C",
        "capacity": 1,
    },
)
check("create_event returns the new event id", isinstance(created.get("id"), int), created)
check(
    "create_event rejects capacity 0",
    "error" in client.call_tool(
        "create_event",
        {"title": "Bad", "description": "", "date": "2026-09-18", "venue": "Room D", "capacity": 0},
    ),
)

client.call_tool("register_attendee", {"event_id": created["id"], "name": "First Seat", "email": "first@example.com"})
full = client.call_tool("register_attendee", {"event_id": created["id"], "name": "Late Comer", "email": "late@example.com"})
check("full event returns 'Event is full'", full.get("error") == "Event is full", full)
check(
    "check_availability on unknown event returns an error",
    "error" in client.call_tool("check_availability", {"event_id": 9999}),
)
check("get_event_summary on unknown event returns an error", "error" in client.call_tool("get_event_summary", {"event_id": 9999}))

client.close()

print()
print(f"{len(failures)} failure(s)" if failures else "ALL CHECKS PASSED")
sys.exit(1 if failures else 0)
