# Extend a Managed Agent with an MCP Server and a Skill

Give one Managed Agent a documentation server and a document skill, then read its event log to see which extension served each call. You run the same task three times: bare, extended, and extended with the approval gate left on.

| Step | What you configure | What you get |
|------|--------------------|--------------|
| 1 | An environment and a baseline Agent | A container that may reach MCP servers and an Agent with the built-in toolset only |
| 2 | The baseline turn | The event log of a task that names a docs search and a skill neither of which exists yet |
| 3 | `mcp_servers`, an `mcp_toolset` grant and a permission policy | `agent.mcp_tool_use` events from Microsoft Learn |
| 4 | `skills` and a download | A skill read in the log and a `.docx` on disk |
| 5 | An audit script | A tally of container, MCP and skill calls per session |
| 6 | The grant without `default_config` | A Session parked at `requires_action` |
| 7 | Cleanup | Every session and environment deleted |

## Before You Start

**Steps 2, 3, 4 and 6 spend money.** Managed Agents bills model tokens plus session-hours, and each of those four steps runs one Session. You need a funded Claude Console account and an API key; nothing in this lab works against a mock.

| Part | Runnable now | Needs |
|------|--------------|-------|
| Setup: install and import check | Yes, offline and free | Python 3.11+ |
| Steps 1 to 4, 6, 7 | Yes, billed | `ANTHROPIC_API_KEY` in `demos/10-sdk-managed-agents/.env`, network access to `api.anthropic.com` |
| Step 5: audit | Yes, reads sessions that already exist | The session IDs printed by Steps 2 and 4 |

The Microsoft Learn MCP endpoint is public and needs no credentials, so the lab uses no vault. This lab builds on [Extend an Agent with MCP Servers and Skills](../../demos/10-sdk-managed-agents/06-tools-mcp/readme.md); the concepts live there and the steps below link back to them.

---

## Where to Open Claude Code

Open Claude Code inside the lab starter. Nothing in this lab writes to `.claude/`; the Agents, environments and Sessions live in the cloud, and the only local files are the helper module and the scripts you write beside it. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/10-sdk-managed-agents/05-extend/docs-agent
claude
```

Every terminal command below expects a shell sitting in `docs-agent/`, because the `parents[4]` loader in `common.py` counts its way to the repo root from there.

---

## Setup

The starter ships `common.py`, which loads the key and provides the helpers every script shares: `send_task` posts a user message, `record_run` remembers a session and its environment for the cleanup step, and `watch` polls the event log and hands each new event to a function you pass in.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -c "import common; print('ready', common.suffix)"
```

On Linux or macOS the interpreter is `.venv/bin/python`.

**Expected result:** one line, `ready` followed by an eight character hex suffix. An `ImportError` on `anthropic` means the install went into a different interpreter than the one you ran.

---

## Step 1: Create the Environment and the Baseline Agent

An extension is only visible against a reference, so the first Agent carries the built-in toolset and nothing else. Its environment already allows MCP traffic, because a `limited` container denies all egress and a later step would otherwise fail on the container before it ever reached the Agent.

Create `baseline.py`:

```python
from common import client, here, record_run, send_task, suffix, text_of, watch

TASK = (
    "Search Microsoft Learn for what Azure Container Apps bills for. "
    "Then use the docx skill to write "
    "/mnt/session/outputs/container-apps-brief.docx with a heading, "
    "three bullet findings, and the doc URLs you used."
)

environment = client.beta.environments.create(
    name=f"docs-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "limited", "allow_mcp_servers": True}},
)
print(f"environment  {environment.id}")

agent = client.beta.agents.create(
    name=f"docs-baseline-{suffix}",
    model="claude-sonnet-5",
    system="You research Microsoft documentation and turn the findings into a document.",
    tools=[{"type": "agent_toolset_20260401"}],
)
print(f"agent        {agent.id}  version={agent.version}")
```

`allow_mcp_servers` is the networking half of an MCP connection; the Agent half arrives in Step 3. The task names a docs search and the `docx` skill on purpose: it is the same task in every run, so any difference in the log comes from the Agent's configuration alone.

**Expected result:** the script prints an `environment` line and an `agent` line with `version=1`. Nothing is billed yet because no Session exists.

---

## Step 2: Run the Baseline Turn

Append the session, the task and a printer to `baseline.py`. The printer is the first half of the lab's skill: every tool call is one `agent.tool_use` line with its name and the first characters of its input.

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Baseline turn",
)
record_run(session.id, environment.id)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")


def show(event):
    if event.type == "agent.tool_use":
        print(f"  tool_use      {event.name} {str(event.input)[:70]}")
    elif event.type == "agent.mcp_tool_use":
        print(f"  mcp_tool_use  {event.name} {event.input}")
    elif event.type == "agent.message":
        print(f"  message       {text_of(event.content)[:200]}")
    elif event.type == "session.status_idle":
        print(f"  status_idle   stop_reason={event.stop_reason.type}")


send_task(session.id, TASK)
watch(session.id, show)
```

```bash
.venv/Scripts/python baseline.py
```

**Expected result:** a handful of `tool_use` lines and a final `status_idle   stop_reason=end_turn`, with no `mcp_tool_use` line anywhere. The Agent has no docs server and no skill, so it substitutes what it does have: expect calls to `web_search`, `web_fetch` or `bash` standing in for the docs search (the `limited` container may refuse some of them), and `bash` calls hunting for a skill directory or writing the document with a library. Your exact lines differ, so copy the printed `session` ID into a note called `baseline`; Step 5 reads it back.

The absence is the lesson. The task asked for two capabilities and got a workaround for each, which is what an Agent does when an extension point is missing.

---

## Step 3: Declare the MCP Server and Its Grant

An MCP server reaches the Agent through two entries that must agree. `mcp_servers` names the connection and carries no credentials; a matching `mcp_toolset` entry in `tools` grants access and sets the permission policy. A declared server with no toolset is a validation error.

Create `extend.py` by copying `baseline.py`, then rename the session title to `Extended turn` and replace the `agent` block with this one:

```python
agent = client.beta.agents.create(
    name=f"docs-extended-{suffix}",
    model="claude-sonnet-5",
    system="You research Microsoft documentation and turn the findings into a document.",
    mcp_servers=[
        {
            "type": "url",
            "name": "microsoft-learn",
            "url": "https://learn.microsoft.com/api/mcp",
        }
    ],
    tools=[
        {"type": "agent_toolset_20260401"},
        {
            "type": "mcp_toolset",
            "mcp_server_name": "microsoft-learn",
            "default_config": {"permission_policy": {"type": "always_allow"}},
        },
    ],
)
```

`mcp_server_name` must equal the `name` above it. The `default_config` line is the permission policy: MCP tools default to `always_ask`, so without it every call would park the Session, which Step 6 shows on purpose.

```bash
.venv/Scripts/python extend.py
```

**Expected result:** the log now contains `mcp_tool_use  microsoft_docs_search {...}` with a query about Container Apps billing, and the generic `web_search` stand-in is gone. The run still ends at `end_turn`; the skill is not attached yet, so the document step falls back to the same workaround as in Step 2.

---

## Step 4: Attach the Skill and Download the Document

A skill is a documented procedure for tools the Agent already has. Attaching one costs the model only its name and description; the full `SKILL.md` enters context when the task calls for it, and that read shows up in the log as an ordinary `read` of `/workspace/skills/docx/SKILL.md`.

Add one field to the `agents.create` call in `extend.py`, beside `mcp_servers`:

```python
    skills=[{"type": "anthropic", "skill_id": "docx"}],
```

Then append the download after the `watch` call. Files the Agent writes to `/mnt/session/outputs/` are captured by the Files API; indexing lags the idle event, so the loop retries before giving up.

```python
output_dir = here / "outputs"
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
```

The loop needs `import time` at the top of the file. Run `extend.py` again.

```bash
.venv/Scripts/python extend.py
```

**Expected result:** the log now has a `tool_use  read {'file_path': '/workspace/skills/docx/SKILL.md'}` line before any file is written, followed by the Agent building the document and usually rendering it back to check the layout. The script ends with `[downloaded] outputs/container-apps-brief.docx`. Open the file: it has a heading, three bullets and the Microsoft Learn URLs the `mcp_tool_use` calls returned. Copy this run's `session` ID into a note called `extended`.

A failed download with an empty `outputs` list after five tries means indexing lagged unusually long; rerun only the listing against the same session; the whole script is not needed.

---

## Step 5: Audit Which Extension Served Each Call

The log separates the two extension points. An `agent.mcp_tool_use` event ran on the orchestration layer against a connected server. An `agent.tool_use` event ran in the container, and when its input points at `/workspace/skills/` it is the skill at work: the `SKILL.md` read, and any helper script the skill ships.

Create `audit.py`. It takes a session ID, reads the finished log without starting anything, and prints one routed line per call plus a tally:

```python
import sys
from collections import Counter

from common import client

session_id = sys.argv[1]
tally = Counter()

for event in client.beta.sessions.events.list(session_id, order="asc"):
    if event.type == "agent.mcp_tool_use":
        route = "mcp"
        label = f"{event.name} {event.input}"
    elif event.type == "agent.tool_use":
        route = "skill" if "/workspace/skills/" in str(event.input) else "container"
        label = f"{event.name} {str(event.input)[:70]}"
    else:
        continue
    tally[route] += 1
    print(f"  [{route:<9}] {label}")

print(f"\ncontainer={tally['container']} mcp={tally['mcp']} skill={tally['skill']}")
```

Run it against both sessions you noted.

```bash
.venv/Scripts/python audit.py <baseline session id>
.venv/Scripts/python audit.py <extended session id>
```

**Expected result:** the baseline session ends with `mcp=0 skill=0` and every call under `container`. The extended session shows `mcp` at one or more, `skill` at one or more, and a smaller `container` share, because work the container did by hand in Step 2 now belongs to the server and the skill. The two tallies side by side are the receipt that each extension changed where the calls went.

---

## Step 6: Drop the Policy and Park the Session

The permission policy is the setting that decides whether an MCP call runs unattended. Remove it and the toolset falls back to `always_ask`: the first MCP call arrives with `evaluated_permission` of `ask` and the Session stops until someone answers. Answering is the subject of [Gate an Agent on Human Approval](../../demos/10-sdk-managed-agents/07-human-in-the-loop/readme.md); here you only watch it park.

Create `gated.py` by copying `extend.py`, drop the download block, and change the grant to a bare entry:

```python
        {"type": "mcp_toolset", "mcp_server_name": "microsoft-learn"},
```

Replace the `show` function and the `watch` call so the printer reports the pending call and the watch returns at the gate:

```python
def show(event):
    if event.type == "agent.mcp_tool_use":
        print(f"  mcp_tool_use  {event.name} permission={getattr(event, 'evaluated_permission', None)}")
    elif event.type == "agent.mcp_tool_result":
        print("  mcp_tool_result")
    elif event.type == "session.status_idle":
        print(f"  status_idle   stop_reason={event.stop_reason.type}")
        if event.stop_reason.type == "requires_action":
            print(f"  waiting on    {event.stop_reason.event_ids}")


send_task(session.id, TASK)
watch(session.id, show, stop_on_requires_action=True)
print(f"status       {client.beta.sessions.retrieve(session.id).status}")
```

```bash
.venv/Scripts/python gated.py
```

**Expected result:** one `mcp_tool_use  microsoft_docs_search permission=ask` line, no `mcp_tool_result`, then `status_idle   stop_reason=requires_action` and a `waiting on` line listing the ID of that tool call. The script exits with the Session still idle and no document written. The same poll loop that returned at `end_turn` in Steps 2 to 4 returns here only because `stop_on_requires_action` is on; without it, `watch` keeps polling a Session nobody is going to answer.

---

## Step 7: Clean Up

Each script recorded its session and environment in `runs.json`. Sessions go first, because an environment with a live session cannot be removed. The Agents stay published and cost nothing at rest.

Create `cleanup.py`:

```python
import json

from common import client, runs_file

runs = json.loads(runs_file.read_text())

for run in runs:
    client.beta.sessions.delete(run["session"])
    print(f"deleted session      {run['session']}")

for environment_id in sorted({run["environment"] for run in runs}):
    client.beta.environments.delete(environment_id)
    print(f"deleted environment  {environment_id}")

runs_file.unlink()
print(f"removed      {runs_file.name}")
```

```bash
.venv/Scripts/python cleanup.py
```

**Expected result:** one `deleted session` line per run (four after this lab: baseline, the two `extend.py` runs, and `gated.py`), one `deleted environment` line per environment, and `removed      runs.json`. `outputs/container-apps-brief.docx` stays on disk.

---

## Verification

A successful lab run produces all of the following:

- `baseline.py` ends at `end_turn` with no `mcp_tool_use` line
- `extend.py` logs a `microsoft_docs_search` MCP call and a `read` of `/workspace/skills/docx/SKILL.md`, and downloads `outputs/container-apps-brief.docx`
- `audit.py` reports `mcp=0 skill=0` for the baseline session and non-zero `mcp` and `skill` for the extended one
- `gated.py` ends with `stop_reason=requires_action`, `permission=ask` and no `mcp_tool_result`
- `cleanup.py` deletes every session and environment it recorded

## Common Failures

| Symptom | Cause |
|---|---|
| 400 when the session is created | The environment is `limited` without `allow_mcp_servers` or an `allowed_hosts` entry for the server |
| 400 or validation error when the Agent is created | `mcp_servers` declares a server that no `mcp_toolset` names, or `mcp_server_name` does not match its `name` |
| `extend.py` stops after `requires_action` and prints no result | The `default_config` permission policy is missing from the grant |
| The log shows no `read` of `SKILL.md` | The skill is not in `skills`, or the task did not name the skill |
| The Agent is rejected with `skills` set | The `tools` list was cleared; skills need the `read` tool from the built-in toolset |
| `outputs` is empty after the turn | File indexing lagged the idle event; widen the retry loop in Step 4 |
| `UnicodeEncodeError: 'charmap' codec` mid-stream | The Windows console is on `cp1252`; keep the `sys.stdout.reconfigure(encoding="utf-8")` line in `common.py` |
| `FileNotFoundError: runs.json` in `cleanup.py` | No script has recorded a run yet |
