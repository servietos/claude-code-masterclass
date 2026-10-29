import os
import sys
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[4] / "demos" / "10-sdk-managed-agents" / ".env")
sys.stdout.reconfigure(encoding="utf-8")

client = Anthropic()
suffix = uuid4().hex[:8]
here = Path(__file__).parent

COMMIT_CHANGES = {
    "type": "custom",
    "name": "commit_changes",
    "description": "Stages every modified file and creates one commit on the current branch.",
    "input_schema": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Commit message"},
            "summary": {"type": "string", "description": "One line per changed file"},
        },
        "required": ["message"],
    },
}

agent_id = os.environ.get("MANAGED_AGENT_ID")
if agent_id:
    agent = client.beta.agents.retrieve(agent_id)
    print(f"agent        {agent.id}  version={agent.version}  (reused)")
else:
    agent = client.beta.agents.create(
        name=f"calc-triage-gated-{suffix}",
        model="claude-opus-4-8",
        system=(
            "You are a test-driven debugger. Fix the failing tests, then call "
            "commit_changes once the suite is green. Never claim a commit landed "
            "before the tool result confirms it."
        ),
        tools=[{"type": "agent_toolset_20260401"}],
    )
    print(f"agent        {agent.id}  version={agent.version}")

gated = client.beta.agents.update(
    agent.id,
    version=agent.version,
    tools=[{"type": "agent_toolset_20260401"}, COMMIT_CHANGES],
)
print(f"version      {gated.version}  (commit_changes added, toolset re-declared)")

uploads = {}
for name in ("calc.py", "test_calc.py"):
    with (here / name).open("rb") as handle:
        uploads[name] = client.beta.files.upload(file=(name, handle, "text/x-python"))

environment = client.beta.environments.create(
    name=f"calc-triage-gate-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)

session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": gated.version},
    environment_id=environment.id,
    title="Calc triage with approval gate",
    resources=[
        {
            "type": "file",
            "file_id": uploads[name].id,
            "mount_path": f"/mnt/session/uploads/{name}",
        }
        for name in ("calc.py", "test_calc.py")
    ],
)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

prompt = (
    "Copy /mnt/session/uploads/calc.py and test_calc.py into a git repository, "
    "make every test pass, then call commit_changes with a conventional commit message."
)
pending = {}

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
    for event in stream:
        if event.type == "agent.message":
            print("".join(block.text for block in event.content))
        elif event.type == "agent.tool_use":
            print(f"[tool] {event.name}")
        elif event.type == "agent.custom_tool_use":
            pending[event.id] = event
            print(f"[pending] {event.id} {event.name}")
            for key, value in event.input.items():
                print(f"  {key}: {value}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

            results = []
            for blocked_id in event.stop_reason.event_ids:
                call = pending[blocked_id]
                verdict = input(f"  Approve {call.name}? [y/n] ").strip().lower()
                if verdict == "y":
                    results.append(
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": blocked_id,
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Committed: {call.input['message']}",
                                }
                            ],
                        }
                    )
                else:
                    results.append(
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": blocked_id,
                            "is_error": True,
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Operator denied the commit. Do not retry; "
                                        "print the diff and stop."
                                    ),
                                }
                            ],
                        }
                    )
                print(f"  verdict: {'allow' if verdict == 'y' else 'deny'}")

            client.beta.sessions.events.send(session.id, events=results)

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
for upload in uploads.values():
    client.beta.files.delete(upload.id)
print("\nDeleted the session, the environment, and the uploads.")
