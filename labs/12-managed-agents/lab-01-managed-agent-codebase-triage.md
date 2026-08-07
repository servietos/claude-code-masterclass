# Build a Managed Agent for Codebase Triage

Build a Managed Agent that fixes three planted bugs in a small Python repo, then add a human approval gate before any commit lands.

| Step | What you configure | What you get |
|------|--------------------|--------------|
| 1 | Agent definition | A cloud-hosted Agent pinned to `agent_toolset_20260401` |
| 2 | Environment | A reusable cloud container with Python and network access |
| 3 | Session with mounts | The broken repo dropped into `/mnt/session/uploads/` |
| 4 | SSE fix loop | Read, edit, run, repeat until all tests pass |
| 5 | Custom commit tool | A protected `commit_changes` tool that pauses on call |
| 6 | Console tracing | A visual replay of the session event timeline |
| 7 | Cleanup | Session and Environment deleted, Agent left published |
| 8 | Stretch | A Session pinned to a specific Agent version |

## Before You Start

**Steps 1 to 8 spend money.** Managed Agents bills session-hours plus model tokens, so every step past Setup needs a funded Claude Console account. There is no waitlist and no beta allowlist: the [quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart) lists exactly two prerequisites, a Console account and an API key. If you do not have one, read the guide and run the solution scripts later; nothing here works against a mock.

What runs where:

| Part | Runnable now | Needs |
|------|--------------|-------|
| Setup: install and `pytest` | Yes, offline and free | Python 3.11+ |
| Steps 1 to 5, 7, 8 | Yes, billed | `ANTHROPIC_API_KEY` in `demos/12-managed-agents/.env` and network access to `api.anthropic.com` |
| Step 6: Console trace | No, browser only | A Console login |

This lab drives the API through the **`anthropic` Python SDK**, the same surface the [module demos](../../demos/12-managed-agents/readme.md) use. Anthropic also ships an [`ant` CLI](https://platform.claude.com/docs/en/api/sdks/cli) that exposes the same resources as shell subcommands; it is the better tool for version-controlled agent YAML, but this repo's devcontainer does not install it, so the lab stays on the SDK. Neither the SDK nor the CLI is preinstalled: you install the SDK in Setup.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/12-managed-agents/01-triage/calc-triage
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `calc-triage` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/12-managed-agents/01-triage/calc-triage write triage.py, which creates the Agent, the Environment and the Session ....
```

That works for every step whose result is just files, and here that is all of them: this lab writes no `.claude/skills/`, no `.claude/settings.json` hooks, no `.claude/commands/`, no `.claude/agents/` and no `.mcp.json`, so nothing depends on the launch directory. The terminal work does: the venv, `pytest` and every driver run expect a shell sitting in `calc-triage/`, and the `parents[4]` loader counts its way to the repo root from there. Launch inside `calc-triage` from Step 1 onward.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

Nothing in this lab belongs in the repository's `.claude/` directory. The Agent, the Environment and the Session all live in the cloud; the only local files are the Python fixture and the driver scripts you write beside it.

---

## Setup

The fixture is checked in for you. `calc.py` ships three functions, each carrying a one-line docstring that states its contract and exactly one bug that violates it, and `test_calc.py` ships one pytest test per bug. Install the dependencies and confirm the fixture is broken in exactly three places:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q
```

On Linux or macOS use `.venv/bin/python` instead of `.venv/Scripts/python`.

**Expected result:** `3 failed`, one per planted bug. That is the starting state, and it stays the starting state: the Files API uploads a copy, so the agent edits the container's `calc.py` and never touches yours. What you write in this lab is the two driver scripts beside the fixture, `triage.py` and `gated_commit.py`; the completed reference for both is [`01-triage/calc-triage-solution/`](01-triage/calc-triage-solution/readme.md).

Verified on Python 3.12.10:

```text
FAILED test_calc.py::test_median_averages_the_two_middle_values - assert 3 ==...
FAILED test_calc.py::test_percent_change_rejects_a_zero_baseline - ZeroDivisi...
FAILED test_calc.py::test_running_total_is_inclusive - assert [0, 1, 3] == [1...
3 failed in 0.04s
```

The key lives in [`demos/12-managed-agents/.env`](../../demos/12-managed-agents/), which is git-ignored, shared with every demo in the module. Create it if the module demos have not already, and paste your own key into it:

```text
ANTHROPIC_API_KEY=sk-ant-api03-...
```

There is nothing to export and nothing to source. Every driver script you write in this lab opens with the same two lines, and the path resolves from the script's own location, so a run works from any working directory:

```python
load_dotenv(Path(__file__).resolve().parents[4] / "demos" / "12-managed-agents" / ".env")
sys.stdout.reconfigure(encoding="utf-8")
```

`parents[4]` walks `calc-triage/`, `01-triage/`, `12-managed-agents/`, `labs/` and lands on the repo root. The second line is not decoration on Windows: the agent narrates its own fixes in prose containing arrows and dashes, and a default `cp1252` console raises `UnicodeEncodeError` mid-stream, after the Session is already created and billing.

To check the credential the SDK will actually resolve, run `ant auth status` if you have the CLI; otherwise a failed call returns `401 authentication_error`, which is a clear enough signal.

---

## Step 1: Create the Agent

Open a new `triage.py` with the preamble every script in this lab shares:

```python
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
```

Then create a test-driven debugging agent pinned to the bundled toolset:

```python
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
```

Capture **both** the ID and the version. Agent IDs are `agent_`-prefixed, and `version` is the integer you need in Step 5 to update the Agent safely. The random `suffix` keeps `name` unique across runs, which matters more in Step 2 than here.

**Expected result:** an `agent_...` identifier and version `1`.

```text
agent        agent_01WTMDpzo2Ei3zGjEnNJ41oJ  version=1
```

`model`, `system` and `tools` live on the Agent, never on the Session; that split is what makes the Agent reusable across runs. The toolset bundles bash, read, write, edit, glob, grep, web_fetch and web_search, which is everything the fix loop needs.

---

## Step 2: Create the Environment

Create a cloud Environment with unrestricted networking so the agent can `pip install pytest`:

```python
environment = client.beta.environments.create(
    name=f"calc-triage-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)
print(f"environment  {environment.id}")
```

`name` is required and must be unique in your workspace; a duplicate returns `409`. That is why the name carries the same `suffix`: without it, the second run of the lab fails before it reaches the agent.

**Expected result:** an `env_...` identifier.

```text
environment  env_01YSdQDHcm5UefKhNXkB5hSS
```

`type` and `networking` are fields inside `config`, not top-level arguments. The Environment is a reusable container template: you pay the cold-start cost once and bind it to as many Sessions as the lab needs.

---

## Step 3: Mount the Broken Repo

Upload the two files. The Files API takes one file per call, so this is two calls:

```python
uploads = {}
for name in ("calc.py", "test_calc.py"):
    with (here / name).open("rb") as handle:
        uploads[name] = client.beta.files.upload(file=(name, handle, "text/x-python"))
    print(f"file         {name}  {uploads[name].id}")
```

Open a Session that mounts each upload as its own resource:

```python
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
```

**Expected result:** a `sesn_...` identifier and a trace URL you will open in Step 6. Print that URL now, while you have the ID.

```text
file         calc.py  file_011CdcA1jgAAwjnz4NZB5V5a
file         test_calc.py  file_011CdcA1mXH3vsSg5pQ6vzix
session      sesn_013TVXfFQ9Jx65XFbgDm75By
trace        https://platform.claude.com/workspaces/default/sessions/sesn_013TVXfFQ9Jx65XFbgDm75By
```
 Swap `default` for your workspace ID if your API key does not belong to the org's Default workspace; the Session response does not carry the workspace, so a wrong slug lands on a "Session not found" page with a **Search workspaces** button.

`mount_path` is required and must be absolute. Mounting is a `resources` array on the Session, one entry per file, up to 500 per Session. The Session exists but is idle: no instruction has been sent, so no tokens are billed yet.

---

## Step 4: Run the Fix Loop

Open the stream **before** sending the instruction, then send it while the stream is live:

```python
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
```

Breaking on `session.status_idle` alone is the mistake to avoid. Idle is also how a permission pause presents itself, so the stop reason, not the event type, is what ends the loop.

Watch the stream emit `agent.message` for the plan, then `agent.tool_use` events as the agent reads `calc.py`, edits it, and re-runs `pytest`.

**Expected result:** the Session reaches `session.status_idle` with `stop_reason.type` of `end_turn` once the suite is green.

```text
[tool] bash
[tool] read
[tool] read
[tool] bash
All three tests fail as expected. Let me fix each function per its docstring contract.
[tool] edit
[tool] bash
Median passes. Now `percent_change`:
[tool] edit
[tool] bash
...
Suite is green. Writing the fixed file to outputs:
[tool] bash
All 3 tests pass and the fixed `calc.py` is at `/mnt/session/outputs/calc.py`.
[idle] stop_reason=end_turn
```

The agent's own final `pytest` run reports `3 passed`, because the test file in the starter contains exactly three tests, and that count is yours to control. Iteration count is not: a non-deterministic agent may take two passes or five. Judge the run by the stop reason and the test count, not by how long it took to get there.

The stream has no replay. If your connection drops, reconnect and call `client.beta.sessions.events.list(session.id)` to fill the gap, deduplicating on `event.id`.

`content` is always an array of content blocks, never a bare string. And note that `session.status_idle` is the SSE event name; `session.status_idled` is the **webhook** `data.type` for roughly the same transition. The two namespaces do not overlap, and mixing them is the most common reason a stream handler silently never fires.

---

## Step 5: Add a Human Gate

A custom tool is not gated by a permission policy. Permission policies govern tools Anthropic executes for you; a custom tool has no implementation on Anthropic's side at all, so **you** are the gate. The agent emits `agent.custom_tool_use`, the Session parks at `requires_action`, and nothing proceeds until you answer.

Write this one in a separate `gated_commit.py` so you can run the allow pass and the deny pass independently. It opens with the same preamble as `triage.py` and reuses the published Agent through `MANAGED_AGENT_ID`.

Declare the tool alongside the existing toolset, then publish it as a new Agent version:

```python
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
```

Retrieve or create the Agent, then publish the new version:

```python
gated = client.beta.agents.update(
    agent.id,
    version=agent.version,
    tools=[{"type": "agent_toolset_20260401"}, COMMIT_CHANGES],
)
print(f"version      {gated.version}  (commit_changes added, toolset re-declared)")
```

Re-declaring `agent_toolset_20260401` is not redundant. Array fields on `agents.update` are **replaced wholesale**, so sending only the custom tool would strip bash, read, write and edit, leaving an agent that can call `commit_changes` and nothing else. Passing `version` makes the update optimistically locked: a stale value returns `409` instead of silently overwriting someone else's change.

Open a second Session bound to the new version, re-mounting the same two files:

```python
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
```

Send a prompt that drives the agent to the protected call, recording each pending call as it streams past:

```python
        elif event.type == "agent.custom_tool_use":
            pending[event.id] = event
            print(f"[pending] {event.id} {event.name}")
            for key, value in event.input.items():
                print(f"  {key}: {value}")
```

The stop reason names the blocking event IDs, but the arguments live on the earlier `agent.custom_tool_use` event, so keep the lookup.

When the Session idles with `stop_reason.type` of `requires_action`, answer every ID in `stop_reason.event_ids`. Ask the operator, and build an allow result or a deny result from the answer:

```python
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
```

Run it once answering `y`, then once answering `n`.

**Expected result:** on the allow pass the Session returns to `running` and the agent confirms the commit. On the deny pass it absorbs the rejection and does what the message told it to do instead, rather than aborting or retrying.

```text
[pending] sevt_01JWkKcvnvfSpDMBEVtfyddC commit_changes
  message: fix: correct median, percent_change, and running_total contracts
...
  summary: calc.py: fix median even-length averaging, zero-baseline ValueError, and inclusive running total
[idle] stop_reason=requires_action
  Approve commit_changes? [y/n] n
  verdict: deny
The commit was denied. As instructed, here is the diff, and I'll stop.
[tool] bash
...
[idle] stop_reason=end_turn
```

There is no allow verb and no deny verb here: declining **is** returning a refusal result. The field is `custom_tool_use_id`, not `tool_use_id`; the two event types take different keys and mixing them is a `400`. The script blocks on `input()` at the gate, so run it in a real terminal.

The other gate, the one for tools Anthropic runs, is `permission_policy` of `always_ask` inside the toolset config, answered with `user.tool_confirmation` and `tool_use_id`. Both are demonstrated side by side in [`demo-approval-gate.md`](../../demos/12-managed-agents/05-human-in-the-loop/demo-approval-gate.md).

---

## Step 6: Inspect in the Console

**Not runnable from the terminal.** This step needs a browser and a Console login.

1. Open the trace URL you printed in Step 3, `https://platform.claude.com/workspaces/{workspace}/sessions/{session_id}`. Use the workspace your API key belongs to.

2. Walk the event timeline left to right: `user.message`, then the chain of `agent.tool_use` calls, the `requires_action` pause, the `user.custom_tool_result`, and the final idle.

3. Open the two traces side by side and compare the per-turn input and output counts from `span.model_request_end`. Note where they diverge and write down why you think they do. Prompt caching and per-turn variance make the direction unreliable, so the exercise is reading the numbers, not confirming a prediction.

---

## Step 7: Download the Output and Clean Up

The fixed `calc.py` exists only in the container until you pull it. Session-scoped files include the two you mounted, and those are not downloadable, so filter on the flag rather than taking whatever the list returns first:

```python
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
```

Without the filter the loop hands a mounted input to `files.download` and the run dies with `400 ... is not downloadable`, after the work is finished but before anything is cleaned up. The retry exists for the same reason: an unfiltered list is never empty, so it would return on the first pass whether the agent had written an output or not.

Sessions and Environments are billed cloud resources. Delete them, and the uploads with them:

```python
client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
for upload in uploads.values():
    client.beta.files.delete(upload.id)
print(f"\nDeleted the session, the environment, and the uploads. Agent {agent.id} stays published.")
```

**Expected result:** one file on disk and a clean workspace.

```text
[downloaded] outputs/calc.py  (743 bytes)

Deleted the session, the environment, and the uploads. Agent agent_01WTMDpzo2Ei3zGjEnNJ41oJ stays published.
```

The Agent survives on purpose: it holds `model`, `system` and `tools`, costs nothing at rest, and Step 5 reuses it through `MANAGED_AGENT_ID`. If a run crashed before this block, list what is left with `client.beta.sessions.list()` and `client.beta.environments.list()` and delete by ID.

---

## Step 8: Stretch: Pin a Session to an Agent Version

Every `agents.update` call produces a new version, numbered from 1. Pin a Session to a specific version so a staged rollout does not affect in-flight work:

```python
pinned = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": 1},
    environment_id=environment.id,
)

latest = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
)
```

Passing the bare agent ID as a string uses the latest version at creation time. There is no `version: "latest"` literal: omitting the field **is** the latest-version case. Update the Agent again and verify the pinned Session keeps using version 1 while a new Session picks up the change; Sessions pin, they do not migrate.

The same comparison, run against a `bash` permission policy instead of a custom tool, is in [`demo-agent-versioning.md`](../../demos/12-managed-agents/03-production-features/demo-agent-versioning.md).

---

## Verification

A successful lab run produces all of the following:

- Locally, `pytest` against your starter reports `3 failed`, and against the `calc.py` the agent wrote to `outputs/` reports `3 passed`
- The Step 4 stream ends at `session.status_idle` with `stop_reason.type` of `end_turn`
- The Console trace shows an `agent.custom_tool_use` event followed by a matching `user.custom_tool_result`, once allowed and once denied
- `sessions.list()` and `environments.list()` come back empty of this lab's resources, because Step 7 deleted them
- The deliverable: a screenshot of the Console trace with the gate event highlighted, attached to the lab submission

## Common Failures

| Symptom | Cause |
|---|---|
| `400` on the result event | Used `tool_use_id` instead of `custom_tool_use_id` |
| Agent can no longer read or edit files | `agents.update` replaced `tools` with the custom tool alone |
| `KeyError` on the pending lookup | Did not record `agent.custom_tool_use` while streaming |
| Stream handler never fires | Listening for `session.status_idled`, the webhook name, instead of `session.status_idle` |
| The loop hangs after sending the result | Broke out of the stream before the follow-up turn arrived |
| `400 ... is not downloadable` | Downloaded every session-scoped file instead of filtering on `metadata.downloadable` |
| `UnicodeEncodeError: 'charmap' codec` mid-stream | Windows console left on `cp1252`; call `sys.stdout.reconfigure(encoding="utf-8")` |
| `409` on environment create | Environment name already taken in this workspace |
| Console shows "Session not found" | Wrong workspace slug in the trace URL |
