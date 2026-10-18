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
output_dir = here / "outputs"
regions = ["emea", "americas", "apac"]

uploads = {region: client.files.upload(file=here / "feedback" / f"{region}.csv") for region in regions}
for region, upload in uploads.items():
    print(f"file         {upload.id}  {region}.csv")

lead = client.beta.agents.create(
    name=f"feedback-lead-{suffix}",
    model="claude-opus-5-5",
    system=(
        "You produce the weekly customer feedback digest. Read every regional CSV under "
        "/mnt/session/uploads/feedback/ and write /mnt/session/outputs/feedback-digest.md."
    ),
    tools=[{"type": "agent_toolset_20260401"}],
)
print(f"lead         {lead.id}")

environment = client.beta.environments.create(
    name=f"feedback-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "limited"}},
)
print(f"environment  {environment.id}")

session = client.beta.sessions.create(
    agent=lead.id,
    environment_id=environment.id,
    title="Feedback digest",
    resources=[
        {
            "type": "file",
            "file_id": upload.id,
            "mount_path": f"/mnt/session/uploads/feedback/{region}.csv",
        }
        for region, upload in uploads.items()
    ],
)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

prompt = "Write this week's customer feedback digest from the three regional files."

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
    for event in stream:
        if event.type == "agent.message":
            print("".join(block.text for block in event.content if block.type == "text"))
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
        for metadata in client.beta.files.list(scope_id=session.id, betas=["managed-agents-2026-04-01"])
        if metadata.downloadable
    ]
    if outputs:
        break
    time.sleep(2)

for metadata in outputs:
    client.files.download(metadata.id).write_to_file(output_dir / metadata.filename)
    print(f"[downloaded] outputs/{metadata.filename}  ({metadata.size_bytes} bytes)")

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
for upload in uploads.values():
    client.files.delete(upload.id)
print("\nDeleted the session, the environment, and the uploaded files.")
