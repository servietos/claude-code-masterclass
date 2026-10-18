import json
import sys
import time
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[4] / "demos" / "10-sdk-managed-agents" / ".env")
sys.stdout.reconfigure(encoding="utf-8")

client = Anthropic()
suffix = uuid4().hex[:8]
here = Path(__file__).parent
output_dir = here / "outputs"
stores_file = here / "stores.json"
fixture = ["inventory.py", "test_inventory.py"]

CHECKLIST = """# Review checklist

- Every finding names the file and line, for example inventory.py:21.
- Every finding carries a severity: critical, major or minor.
- SQL built from user input is critical.
- A function that breaks its own docstring contract is major.
- Every finding proposes a concrete fix in one or two lines of code.
"""

RUBRIC = """# Review rubric

- /mnt/session/outputs/review.md exists and is Markdown.
- It has one section per finding, and no two sections describe the same defect.
- The review flags the SQL query in find_by_sku that is built from the sku with an f-string, as critical.
- The review flags that restock accepts zero or negative amounts although its docstring requires a ValueError.
- The review flags that low_stock compares with < although its docstring says at or below the reorder level.
- Every finding names the file and line, carries a severity, and proposes a fix.
- The review ends with a short list of the tests that would catch each finding.
"""


def text_of(blocks):
    return " ".join(block.text for block in blocks if block.type == "text")


if stores_file.exists():
    stores = json.loads(stores_file.read_text())
    print(f"stores       reused from {stores_file.name}")
else:
    conventions = client.beta.memory_stores.create(
        name="Team Conventions",
        description="The team's code review checklist. Reference material: read it, never change it.",
    )
    client.beta.memory_stores.memories.create(conventions.id, path="/review-checklist.md", content=CHECKLIST)
    history = client.beta.memory_stores.create(
        name="Review History",
        description="One dated entry per review run, listing each finding's title and severity.",
    )
    stores = {"conventions": conventions.id, "history": history.id}
    stores_file.write_text(json.dumps(stores, indent=2))
    print(f"stores       created and saved to {stores_file.name}")
print(f"conventions  {stores['conventions']}")
print(f"history      {stores['history']}")

read_only_tools = [
    {
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": False},
        "configs": [{"name": name, "enabled": True} for name in ("read", "glob", "grep")],
    }
]

security = client.beta.agents.create(
    name="Security reviewer",
    description="Read-only reviewer for injection, unsafe input handling and secrets. Give it file paths; it reports findings with file:line.",
    model="claude-sonnet-5-5",
    system=(
        "Review only the files you are pointed at, for security defects: injection, unsafe handling of "
        "user input, secrets in code. Report each finding as file:line, severity and a suggested fix. "
        "Say plainly if you found none. Report only; write no files."
    ),
    tools=read_only_tools,
)
correctness = client.beta.agents.create(
    name="Correctness reviewer",
    description="Read-only reviewer that checks each function against its docstring contract. Give it file paths; it reports findings with file:line.",
    model="claude-haiku-5-5",
    system=(
        "Review only the files you are pointed at. For every function, compare what the code does with what "
        "its docstring promises, and report each mismatch as file:line, severity and a suggested fix. "
        "Report only; write no files."
    ),
    tools=read_only_tools,
)
print(f"security     {security.id}")
print(f"correctness  {correctness.id}")

lead = client.beta.agents.create(
    name=f"review-lead-{suffix}",
    model="claude-opus-5-5",
    system=(
        "You lead code reviews. Send the paths of every file under /mnt/session/uploads/inventory/ to "
        "Security reviewer and to Correctness reviewer at the same time. Check each finding they report "
        "against the code yourself, drop duplicates, apply the checklist in the Team Conventions store, and "
        "write /mnt/session/outputs/review.md. Then append one dated entry to history.md in the Review "
        "History store with each finding's title and severity."
    ),
    tools=[{"type": "agent_toolset_20260401"}],
    multiagent={
        "type": "multiagent_20261001",
        "subagents": {
            "type": "enabled",
            "predefined_agents": [security.id, correctness.id],
            "inline_agents": {"type": "disabled"},
        },
        "workflows": {"type": "disabled"},
    },
)
print(f"lead         {lead.id}")

uploads = {name: client.files.upload(file=here / name) for name in fixture}
for name, upload in uploads.items():
    print(f"file         {upload.id}  {name}")

environment = client.beta.environments.create(
    name=f"review-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "limited"}},
)
print(f"environment  {environment.id}")

session = client.beta.sessions.create(
    agent=lead.id,
    environment_id=environment.id,
    title="Inventory review",
    resources=[
        {"type": "file", "file_id": upload.id, "mount_path": f"/mnt/session/uploads/inventory/{name}"}
        for name, upload in uploads.items()
    ]
    + [
        {
            "type": "memory_store",
            "memory_store_id": stores["conventions"],
            "access": "read_only",
            "instructions": "Apply review-checklist.md to every finding.",
        },
        {
            "type": "memory_store",
            "memory_store_id": stores["history"],
            "access": "read_write",
            "instructions": "Append one dated entry to history.md when the review is written.",
        },
    ],
    budget={"type": "limit", "max_list_cost": {"amount": "800", "currency": "USD"}},
)
print(f"session      {session.id}")
for resource in session.resources:
    if resource.type == "memory_store":
        print(f"mounted      {resource.mount_path}  ({resource.access})")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

outcome = {
    "type": "user.define_outcome",
    "description": "Review inventory.py and test_inventory.py and write the review to /mnt/session/outputs/review.md.",
    "rubric": {"type": "text", "content": RUBRIC},
    "max_iterations": 3,
}

threads = {}
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(session.id, events=[outcome])
    for event in stream:
        if event.type == "agent.message":
            print(text_of(event.content))
        elif event.type == "session.thread_created":
            threads[event.agent_name] = event.session_thread_id
            print(f"[thread] {event.agent_name} {event.session_thread_id}")
        elif event.type == "agent.thread_message_sent":
            print(f"[task -> {event.to_agent_name}] {text_of(event.content)[:100]}")
        elif event.type == "agent.thread_message_received":
            print(f"[report <- {event.from_agent_name}] {text_of(event.content)[:100]}")
        elif event.type == "span.outcome_evaluation_end":
            print(f"[grader] iteration {event.iteration}: {event.result}")
            print(f"         {event.explanation}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

print("\nThreads:")
for thread in client.beta.sessions.threads.list(session.id):
    print(f"  {thread.agent.name:<22} {thread.status}")

if "Security reviewer" in threads:
    print("\nSecurity reviewer's own tool calls:")
    for event in client.beta.sessions.threads.events.list(threads["Security reviewer"], session_id=session.id):
        if event.type == "agent.tool_use":
            print(f"  {event.name} {json.dumps(event.input)[:80]}")

session = client.beta.sessions.retrieve(session.id)
if session.usage.list_cost:
    print(f"\n[cost] {session.usage.list_cost.amount} US cents at list price")

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

for label in ("conventions", "history"):
    print(f"\nVersions in {label}:")
    for version in client.beta.memory_stores.memory_versions.list(stores[label]):
        actor = version.created_by.type if version.created_by else "unknown"
        print(f"  {version.operation:<9} {version.path}  by {actor}")

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
for upload in uploads.values():
    client.files.delete(upload.id)
print("\nDeleted the session, the environment and the uploaded files. Both stores remain for recall.py.")
