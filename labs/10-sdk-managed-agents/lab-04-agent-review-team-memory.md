# Review Code with Specialist Subagents, a Rubric and Team Memory

Build a code review team on Managed Agents: a lead that sends one module to two read-only reviewer subagents, merges their findings against a rubric a grader checks, applies a checklist from a read-only memory store and records the run in a second store that a later session can recall.

| Step | What you configure | What you get |
|------|--------------------|--------------|
| 1 | Two memory stores | A read-only checklist store and a read-write history store, IDs saved to `stores.json` |
| 2 | Two reviewer agents | A security reviewer on Claude Sonnet 5.5 and a correctness reviewer on Claude Haiku 5.5, both read-only |
| 3 | The lead with a `multiagent` block | A Claude Opus 5.5 lead that may delegate to exactly those two |
| 4 | Uploads and an environment | The fixture as session files, a container with limited networking |
| 5 | The session | Two file mounts, both stores with different access modes, an 8.00 USD budget |
| 6 | The outcome | A rubric naming the three defects the review must find |
| 7 | The stream | Tasks, reports and grader verdicts on the primary thread |
| 8 | Thread drill-down | Every thread's status and one reviewer's own tool calls |
| 9 | Download and memory audit | `review.md` on disk and the version history of both stores |
| 10 | A recall session | A new session answering from the Review History store alone |
| 11 | Cleanup | Both stores deleted |

## Before You Start

**Steps 1 to 11 spend money.** Managed Agents bills model tokens at each served model's rate plus 0.08 USD per session-hour while running, and the outcome adds grader iterations; the budget in Step 5 caps the review session at 8.00 USD. You need a funded Claude Console account and an API key; nothing in this lab works against a mock.

| Part | Runnable now | Needs |
|------|--------------|-------|
| Setup: install and `pytest` | Yes, offline and free | Python 3.11+ |
| Steps 1 to 11 | Yes, billed | `ANTHROPIC_API_KEY` in `labs/10-sdk-managed-agents/.env`, network access to `api.anthropic.com`, `anthropic` 1.15.0 or later |

This lab builds on the multiagent, outcome and memory store concepts of [topic 08](../../demos/10-sdk-managed-agents/08-agent-multiagent/readme.md). Read its readme first; the steps below link back to it for the concepts.

---

## Where to Open Claude Code

Open Claude Code inside the lab starter. Nothing in this lab writes to `.claude/`; the agents, the environment, the session and both memory stores live in the cloud, and the only local files are the fixture and the three driver scripts you write beside it. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/10-sdk-managed-agents/04-agent-multiagent/review-team
claude
```

Every terminal command below also expects a shell sitting in `review-team/`, because the `parents[2]` loader counts its way to `labs/10-sdk-managed-agents/` from there.

---

## Setup

The fixture is checked in. `inventory.py` holds four functions over SQLite, and three of them carry one planted defect each: a query built from user input, a missing guard its docstring promises, and an off-by-one comparison. `test_inventory.py` has one test per defect.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q
```

On Linux or macOS the interpreter is `.venv/bin/python`.

**Expected result:** `3 failed`, one per defect. Verified on Python 3.12.10:

```text
FAILED test_inventory.py::test_find_by_sku_treats_the_sku_as_data - assert ('...
FAILED test_inventory.py::test_restock_rejects_a_negative_amount - Failed: DI...
FAILED test_inventory.py::test_low_stock_includes_items_at_their_reorder_level
3 failed in 0.08s
```

The reviewers only read the uploaded copy, so these three failures stay the starting state for every run. The completed scripts are in [`04-agent-multiagent/review-team-solution/`](04-agent-multiagent/review-team-solution/readme.md).

---

## Step 1: Seed the Two Memory Stores

Open a new `review.py` with the preamble every script in this lab shares:

```python
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
output_dir = here / "outputs"
stores_file = here / "stores.json"
fixture = ["inventory.py", "test_inventory.py"]
```

Below it, paste the team checklist, which goes into the conventions store, and the review rubric the grader uses in Step 6:

```python
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
```

Then create the two stores once and reuse them on every later run. The checklist is reference material, and the history starts empty because the lead writes it:

```python
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
```

The store `description` is shown to the agent, so it is written for the model. The SDK sends the `agent-memory-2026-07-22` header on these calls by itself.

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

---

## Step 2: Create Two Read-Only Reviewers

Each reviewer gets a narrow system prompt, a model sized to its job, and three read tools. The lead chooses whom to spawn from each agent's `name` and `description`, so write both for the lead to read.

```python
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
```

`default_config` with `enabled` set to `False` switches the whole toolset off, and `configs` turns back on exactly the tools listed, so neither reviewer can run `bash` or write a file.

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

---

## Step 3: Create the Lead with a Multiagent Block

The lead runs on Claude Opus 5.5 and keeps the judgement: it checks every reported finding against the code before it lands in the review. Its system prompt says exactly what to delegate, to whom, and what to keep.

```python
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
```

Turning `inline_agents` off limits delegation to the two agents you listed, and `workflows` is switched off by name because it defaults to enabled on `multiagent_20261001`. Listing an agent that has its own `multiagent` block fails here with a 400: delegation is one level deep.

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

---

## Step 4: Upload the Fixture and Create the Environment

The reviewers need no network, so the environment uses `limited` networking with no hosts allowed.

```python
uploads = {name: client.files.upload(file=here / name) for name in fixture}
for name, upload in uploads.items():
    print(f"file         {upload.id}  {name}")

environment = client.beta.environments.create(
    name=f"review-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "limited"}},
)
print(f"environment  {environment.id}")
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

---

## Step 5: Create the Session with Both Stores and a Budget

Memory stores attach only here, at session creation, next to the file mounts. The conventions store is mounted `read_only`, which the filesystem enforces, and the history store `read_write`, so it is the only one the session can change.

```python
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
```

`amount` is whole US cents as a string, so `"800"` is 8.00 USD, shared by the lead, both reviewers and every grader iteration. A budget cannot be added to a session after it is created.

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

---

## Step 6: Define the Review Outcome

The rubric from Step 1 names the three defects, so the grader can tell a review that found them from one that only sounds thorough. Sending the outcome starts the work; there is no `user.message` in this session.

```python
outcome = {
    "type": "user.define_outcome",
    "description": "Review inventory.py and test_inventory.py and write the review to /mnt/session/outputs/review.md.",
    "rubric": {"type": "text", "content": RUBRIC},
    "max_iterations": 3,
}
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

---

## Step 7: Stream the Tasks, the Reports and the Grader

Open the stream before sending the outcome, then print the events that show the team at work. The script also remembers each reviewer's thread ID for Step 8.

```python
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
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

A `needs_revision` verdict keeps the session running into the next iteration, so the loop's exit stays the idle check. If the run stops at `budget_reached`, the cap was hit before the grader was satisfied; raise it with `client.beta.sessions.update()` to resume.

---

## Step 8: Drill into the Threads

The primary stream showed each reviewer's task and report; the reasoning stays on the reviewer's own thread. Every thread keeps its own event log, and listing it shows what the reviewer actually opened.

```python
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
```

The thread list includes the primary thread, whose `parent_thread_id` is `None`. Compare the session's list cost with your budget before you change any model in Step 2.

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

---

## Step 9: Download the Review and Audit the Stores

Session-scoped files include the two inputs you mounted, which are not downloadable, so filter on the flag. Then list the versions of both stores: the history store gains versions written by the session, and the conventions store keeps only the one your seeding call created.

```python
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
```

```bash
.venv/Scripts/python review.py
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

A write the agent makes through the mount is attributed to the session (`session_actor`), which separates the agent's writes from the ones your own code made. That attribution is the audit trail a reviewer of the reviewers asks for.

---

## Step 10: Recall the History from a New Session

A memory store outlives every session that mounts it. Write `recall.py`: a plain agent, no subagents, the history store mounted `read_only`, and a question the agent can answer only from what Step 9's session wrote.

```python
import json
import sys
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
sys.stdout.reconfigure(encoding="utf-8")

client = Anthropic()
suffix = uuid4().hex[:8]
stores = json.loads((Path(__file__).parent / "stores.json").read_text())

historian = client.beta.agents.create(
    name=f"review-historian-{suffix}",
    model="claude-opus-5-5",
    system="You answer questions about earlier code reviews from the Review History store. Cite the dates of the entries you use.",
    tools=[{"type": "agent_toolset_20260401"}],
)
print(f"historian    {historian.id}")

environment = client.beta.environments.create(
    name=f"recall-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "limited"}},
)

session = client.beta.sessions.create(
    agent=historian.id,
    environment_id=environment.id,
    title="Review recall",
    resources=[{"type": "memory_store", "memory_store_id": stores["history"], "access": "read_only"}],
)
print(f"session      {session.id}\n")

question = "What did earlier reviews of inventory.py find, and which finding had the highest severity?"

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": question}]}],
    )
    for event in stream:
        if event.type == "agent.message":
            print(" ".join(block.text for block in event.content if block.type == "text"))
        elif event.type == "agent.tool_use":
            print(f"[tool] {event.name}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
print("\nDeleted the session and the environment.")
```

```bash
.venv/Scripts/python recall.py
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

This session asks a question and expects an answer, so it opens with a `user.message`; an outcome belongs to sessions whose job is one checkable deliverable.

---

## Step 11: Clean Up

`review.py` and `recall.py` already delete their sessions, environments and uploads. The stores remain until you delete them; write `cleanup.py`:

```python
import json
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = Anthropic()
stores_file = Path(__file__).parent / "stores.json"
stores = json.loads(stores_file.read_text())

for label, store_id in stores.items():
    client.beta.memory_stores.delete(store_id)
    print(f"deleted      {label} {store_id}")
stores_file.unlink()
print(f"removed      {stores_file.name}")
```

```bash
.venv/Scripts/python cleanup.py
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY.

Deleting a store removes its memories and their versions with it. The agents stay published and cost nothing at rest.

---

## Verification

A successful lab run produces all of the following:

- Locally, `pytest` against the starter reports `3 failed`
- The Step 7 stream shows a `[task -> ...]` line for each reviewer and ends at a `span.outcome_evaluation_end` of `satisfied`, followed by `[idle] stop_reason=end_turn`
- `outputs/review.md` names all three defects, each with file, line, severity and fix
- The history store lists at least one version by `session_actor`; the conventions store lists only the version your seeding call created
- `recall.py` answers with the findings and the date of the entry it read
- After `cleanup.py`, `client.beta.memory_stores.list()` no longer returns either store

## Common Failures

| Symptom | Cause |
|---|---|
| `AttributeError: 'Beta' object has no attribute 'memory_stores'` | `anthropic` is older than 0.122.0; the lab pins 1.15.0 or later |
| 400 when the lead is created | `inline_agents` is disabled with an empty `predefined_agents` list, or a listed agent has `multiagent` set itself |
| 400 on session create | The budget `amount` is not a whole number of cents in a string, or a store ID is wrong |
| The lead reviews the code itself | Its system prompt does not name both reviewers or say what to send them |
| The conventions store gained a version by `session_actor` | It was attached `read_write`; reference material belongs `read_only` |
| The run stops at `budget_reached` | Three agents plus grader iterations spent the cap; raise it with `client.beta.sessions.update()` |
| `FileNotFoundError: stores.json` in `recall.py` | `review.py` has not run in this folder yet |
| `UnicodeEncodeError: 'charmap' codec` mid-stream | The Windows console is on `cp1252`; keep the `sys.stdout.reconfigure(encoding="utf-8")` line |
