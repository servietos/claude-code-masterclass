# Walk a Session Through Its Lifecycle

You create each resource in turn, send one message, and poll the Session, because polling makes the state machine visible one transition at a time. Plan for 10 minutes; you finish holding a script that walks the full lifecycle, reads the event log, and deletes the Session and Environment while keeping the Agent.

------

Run it from [`session-lifecycle/`](session-lifecycle/readme.md). The completed reference is [`session-lifecycle-solution/`](session-lifecycle-solution/01-session-lifecycle.py).

## Step 1: Open a Session and Send One Message

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

## Step 2: Poll the State Machine

Poll the Session every two seconds and watch it move from `idle` to `running` and back.

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

**Expected result:** the first poll still reads `idle`, because the session has not picked the turn up yet. That is why the loop breaks on the `session.status_idle` event: breaking on the status alone exits before the agent has answered, and the delete at the end then fails with `Cannot delete session while it is running`. The `stop_reason` check is the second half of the same rule, since a session waiting on a human is idle too. The terminal prints a `status -> running` line within a few seconds, then `status -> idle` once the turn completes, each prefixed with the elapsed seconds.

## Step 3: Read the Event Log

Every persisted event stays queryable after the fact, which is what makes a dropped connection survivable.

```python
for event in log:
    print(f"  {event.type}")
```

**Expected result:** an ordered log along the lines of `user.message`, `session.status_running`, `span.model_request_start`, `agent.message`, `span.model_request_end`, `session.status_idle`. Point out that the `user.message` you sent appears in the log too, because the stream is a shared timeline.
