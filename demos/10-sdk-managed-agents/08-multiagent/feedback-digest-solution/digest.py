import os
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

STYLE_GUIDE = """# Feedback digest style guide

- Open with a summary of exactly three bullets.
- Then one Markdown table with the columns Region, Theme, Mentions, Example tickets.
- Cite ticket ids as they appear in the source, for example EMEA-104.
- Write dates as ISO-8601 (2026-10-05).
- Keep the whole digest under 400 words.
- End with a section titled Open questions.
"""

RUBRIC = """# Feedback digest rubric

- /mnt/session/outputs/feedback-digest.md exists and is Markdown.
- The digest opens with a summary of exactly three bullets.
- It contains one table with the columns Region, Theme, Mentions, Example tickets.
- The table covers all three regions: EMEA, Americas and APAC.
- Every Example tickets cell cites at least one ticket id from that region's file.
- Every date in the digest is written as ISO-8601.
- The digest is under 400 words.
- The digest ends with a section titled Open questions.
"""


def text_of(blocks):
    return " ".join(block.text for block in blocks if block.type == "text")


memory_store_id = os.environ.get("FEEDBACK_MEMORY_STORE_ID")
if not memory_store_id:
    store = client.beta.memory_stores.create(
        name="Report Style",
        description="House style for the weekly feedback digest, plus lessons earlier runs recorded.",
    )
    client.beta.memory_stores.memories.create(store.id, path="/style-guide.md", content=STYLE_GUIDE)
    memory_store_id = store.id
    print(f"memory store {memory_store_id}  (export FEEDBACK_MEMORY_STORE_ID={memory_store_id} to reuse)")
else:
    print(f"memory store {memory_store_id}  (reused)")

uploads = {region: client.files.upload(file=here / "feedback" / f"{region}.csv") for region in regions}
for region, upload in uploads.items():
    print(f"file         {upload.id}  {region}.csv")

reader = client.beta.agents.create(
    name="Feedback reader",
    description="Reads one regional feedback CSV and reports its top themes with mention counts and ticket ids.",
    model="claude-haiku-5-5",
    system=(
        "Read only the CSV file you are pointed at. Report its three most frequent themes, "
        "each with the number of tickets that mention it and two example ticket ids. Report only; write no files."
    ),
    tools=[
        {
            "type": "agent_toolset_20260401",
            "default_config": {"enabled": False},
            "configs": [{"name": name, "enabled": True} for name in ("read", "glob", "grep")],
        }
    ],
)
print(f"reader       {reader.id}")

lead = client.beta.agents.create(
    name=f"feedback-lead-{suffix}",
    model="claude-opus-5-5",
    system=(
        "You produce the weekly customer feedback digest. Delegate each regional CSV under "
        "/mnt/session/uploads/feedback/ to Feedback reader, one file per task, all three at once. "
        "Merge their reports yourself and write /mnt/session/outputs/feedback-digest.md, following the "
        "style guide in the Report Style memory store. When the digest is done, add one line to lessons.md "
        "in that store about this data that a future run should know."
    ),
    tools=[{"type": "agent_toolset_20260401"}],
    multiagent={
        "type": "multiagent_20261001",
        "subagents": {
            "type": "enabled",
            "predefined_agents": [reader.id],
            "inline_agents": {"type": "disabled"},
        },
        "workflows": {"type": "disabled"},
    },
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
    ]
    + [
        {
            "type": "memory_store",
            "memory_store_id": memory_store_id,
            "access": "read_write",
            "instructions": "Read style-guide.md before writing. Read lessons.md if it exists.",
        }
    ],
    budget={"type": "limit", "max_list_cost": {"amount": "500", "currency": "USD"}},
)
print(f"session      {session.id}")
for resource in session.resources:
    if resource.type == "memory_store":
        print(f"mounted      {resource.mount_path}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

outcome = {
    "type": "user.define_outcome",
    "description": "Write this week's customer feedback digest from the three regional files.",
    "rubric": {"type": "text", "content": RUBRIC},
    "max_iterations": 3,
}

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(session.id, events=[outcome])
    for event in stream:
        if event.type == "agent.message":
            print(text_of(event.content))
        elif event.type == "session.thread_created":
            print(f"[thread] {event.agent_name} {event.session_thread_id}")
        elif event.type == "agent.thread_message_sent":
            print(f"[task -> {event.to_agent_name}] {text_of(event.content)[:100]}")
        elif event.type == "agent.thread_message_received":
            print(f"[report <- {event.from_agent_name}] {text_of(event.content)[:100]}")
        elif event.type == "span.outcome_evaluation_start":
            print(f"[grader] iteration {event.iteration} started")
        elif event.type == "span.outcome_evaluation_end":
            print(f"[grader] iteration {event.iteration}: {event.result}")
            print(f"         {event.explanation}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

session = client.beta.sessions.retrieve(session.id)
for evaluation in session.outcome_evaluations:
    print(f"[outcome] {evaluation.outcome_id}: {evaluation.result}")
for thread in client.beta.sessions.threads.list(session.id):
    print(f"[thread] {thread.agent.name} {thread.status}")
if session.usage.list_cost:
    print(f"[cost] {session.usage.list_cost.amount} US cents at list price")

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
print("\nDeleted the session. The memory store outlives it:")
for memory in client.beta.memory_stores.memories.list(memory_store_id, path_prefix="/"):
    if memory.type == "memory":
        print(f"  {memory.path}  ({memory.content_size_bytes} bytes)")
for version in client.beta.memory_stores.memory_versions.list(memory_store_id):
    actor = version.created_by.type if version.created_by else "unknown"
    print(f"  {version.operation:<9} {version.path}  by {actor}")

client.beta.environments.delete(environment.id)
for upload in uploads.values():
    client.files.delete(upload.id)
print("\nDeleted the environment and the uploaded files. The memory store and both agents remain.")
