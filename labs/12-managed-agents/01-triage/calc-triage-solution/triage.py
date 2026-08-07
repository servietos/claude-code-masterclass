import sys
import time
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[4] / "demos" / "12-managed-agents" / ".env")
sys.stdout.reconfigure(encoding="utf-8")

client = Anthropic()
suffix = uuid4().hex[:8]
here = Path(__file__).parent
output_dir = here / "outputs"

uploads = {}
for name in ("calc.py", "test_calc.py"):
    with (here / name).open("rb") as handle:
        uploads[name] = client.beta.files.upload(file=(name, handle, "text/x-python"))
    print(f"file         {name}  {uploads[name].id}")

agent = client.beta.agents.create(
    name=f"calc-triage-{suffix}",
    model="claude-opus-4-8",
    system=(
        "You are a test-driven debugger. Read the failing tests first, then make the "
        "smallest code change that satisfies each docstring contract. Run pytest after "
        "every edit and stop when the suite is green."
    ),
    tools=[{"type": "agent_toolset_20260401"}],
)
print(f"agent        {agent.id}  version={agent.version}")

environment = client.beta.environments.create(
    name=f"calc-triage-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)
print(f"environment  {environment.id}")

session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Calc triage",
    resources=[
        {
            "type": "file",
            "file_id": uploads["calc.py"].id,
            "mount_path": "/mnt/session/uploads/calc.py",
        },
        {
            "type": "file",
            "file_id": uploads["test_calc.py"].id,
            "mount_path": "/mnt/session/uploads/test_calc.py",
        },
    ],
)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

prompt = (
    "Copy /mnt/session/uploads/calc.py and test_calc.py into a working directory, "
    "install pytest, and make every test pass. Run pytest after each edit. "
    "When the suite is green, write the fixed calc.py to /mnt/session/outputs/calc.py."
)

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
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

output_dir.mkdir(exist_ok=True)
outputs = []
for attempt in range(5):
    outputs = [
        metadata
        for metadata in client.beta.files.list(
            scope_id=session.id,
            betas=["managed-agents-2026-04-01"],
        )
        if metadata.downloadable
    ]
    if outputs:
        break
    time.sleep(2)

for metadata in outputs:
    client.beta.files.download(metadata.id).write_to_file(output_dir / metadata.filename)
    print(f"[downloaded] outputs/{metadata.filename}  ({metadata.size_bytes} bytes)")

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
for upload in uploads.values():
    client.beta.files.delete(upload.id)
print(f"\nDeleted the session, the environment, and the uploads. Agent {agent.id} stays published.")
