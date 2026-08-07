# Walk a Session Through Its Lifecycle

You create each resource in turn, send one message, and poll instead of streaming, because polling makes the state machine visible one transition at a time. Plan for 10 minutes; you finish holding a script that walks the full lifecycle, reads the event log, and deletes the Session and Environment while keeping the Agent.

------

Run it from [`session-lifecycle/`](session-lifecycle/readme.md). The completed reference is [`session-lifecycle-solution/`](session-lifecycle-solution/lifecycle.py).

## Step 1: Create the Agent

```python
agent = client.beta.agents.create(
    name=f"lifecycle-explorer-{suffix}",
    model="claude-sonnet-5",
    system="You are a concise assistant. Answer in one short paragraph.",
    tools=[{"type": "agent_toolset_20260401"}],
)
```

**Expected result:** the call returns an object whose `id` starts with `agent_` and whose `version` is `1`, the first entry in that Agent's own version sequence.

## Step 2: Create the Environment

```python
environment = client.beta.environments.create(
    name=f"lifecycle-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)
```

**Expected result:** an `env_` identifier. Environment names must be unique, so a second run with the same literal name returns a 409. The script appends a random suffix for exactly this reason.

## Step 3: Open a Session and Send One Message

Passing the Agent ID as a bare string resolves to its latest version.

```python
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment.id,
    title="Session lifecycle walkthrough",
)

client.beta.sessions.events.send(
    session.id,
    events=[{
        "type": "user.message",
        "content": [{"type": "text", "text": "Compare Claude Code to Claude Cowork"}],
    }],
)
```

**Expected result:** `session.status` reads `idle` immediately after creation, because nothing has been asked of it yet. The script prints a Console trace URL; open it in a browser and leave it visible while the rest of the demo runs.

## Step 4: Poll the State Machine

```python
while True:
    current = client.beta.sessions.retrieve(session.id)
    log = list(client.beta.sessions.events.list(session.id, order="asc"))
    idle = [e for e in log if e.type == "session.status_idle"]
    if current.status == "terminated" or any(
        e.stop_reason.type != "requires_action" for e in idle
    ):
        break
    time.sleep(2)
```

**Expected result:** the first poll still reads `idle`, because the session has not picked the turn up yet. That is why the loop breaks on the `session.status_idle` event rather than on the status field: breaking on the status alone exits before the agent has answered, and the delete at the end then fails with `Cannot delete session while it is running`. The `stop_reason` check is the second half of the same rule, since a session waiting on a human is idle too. The terminal prints `status -> running` within a few seconds, then `status -> idle` once the turn completes.

## Step 5: Read the Event Log

Every persisted event stays queryable after the fact, which is what makes a dropped connection survivable.

```python
for event in log:
    print(f"  {event.type}")
```

**Expected result:** an ordered log along the lines of `user.message`, `session.status_running`, `span.model_request_start`, `agent.message`, `span.model_request_end`, `session.status_idle`. Point out that the `user.message` you sent appears in the log too: the stream is a shared timeline, not a response body.

## Step 6: Hand the Agent ID to the Next Demo

Export the printed Agent ID before the next run:

```bash
export MANAGED_AGENT_ID=agent_...
```

```powershell
$env:MANAGED_AGENT_ID = "agent_..."
```

## Common Failure

If the Session sits at `running` far longer than expected, check the Console trace rather than adding print statements. The trace view replays the same events with span timings, and it will show a stuck tool call immediately.
