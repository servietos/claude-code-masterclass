import os
import time
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = Anthropic()
suffix = uuid4().hex[:8]
# resolved from the script's own location, so the run works from any working directory
here = Path(__file__).parent
csv_path = here / "sales.csv"
output_dir = here / "outputs"

with csv_path.open("rb") as handle:
    # the tuple is the multipart form the SDK expects: filename, open handle, content type
    upload = client.beta.files.upload(file=("sales.csv", handle, "text/csv"))
print(f"file         {upload.id}")

agent_id = os.environ.get("MANAGED_AGENT_ID")
if not agent_id:
    agent = client.beta.agents.create(
        name=f"csv-analyst-{suffix}",
        model="claude-sonnet-5",
        system="You are a senior data analyst. Be concise and quantitative.",
        tools=[{"type": "agent_toolset_20260401"}],
    )
    agent_id = agent.id
    print(f"agent        {agent_id}  (export MANAGED_AGENT_ID={agent_id} to reuse)")
else:
    print(f"agent        {agent_id}  (reused)")

environment = client.beta.environments.create(
    name=f"csv-analyst-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)
print(f"environment  {environment.id}")

session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment.id,
    title="CSV analysis",
    resources=[
        {
            "type": "file",
            "file_id": upload.id,
            "mount_path": "/mnt/session/uploads/sales.csv",
        }
    ],
)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

prompt = (
    "Analyze /mnt/session/uploads/sales.csv and write "
    "/mnt/session/outputs/summary.md with the top 3 insights."
)

seen_event_ids = set()
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
    for event in stream:
        if event.id in seen_event_ids:
            continue
        seen_event_ids.add(event.id)
        if event.type == "agent.message":
            print("".join(block.text for block in event.content))
        elif event.type == "agent.tool_use":
            print(f"[tool] {event.name} {event.input}")
        elif event.type == "span.model_request_end":
            print(f"[usage] {event.model_usage}")
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
client.beta.files.delete(upload.id)
print("\nDeleted the session, the environment, and the uploaded file.")
