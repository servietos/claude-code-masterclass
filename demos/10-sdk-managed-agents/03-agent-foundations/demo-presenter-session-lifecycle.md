---
presents: demo-session-lifecycle.md
budget: 4 min
beats: 3
---

# Present: Walk a Session Through Its Lifecycle

Three resources split by lifetime: the Agent holds the configuration, the Environment is a reusable template, the Session is the disposable running thing. Three beats: the split, the polling loop, and the event log.

------

## Beats

### Beat 1: the Agent carries the configuration, the Session carries a pointer (1 min)

**Open:** [`session-lifecycle/lifecycle.py`](session-lifecycle/lifecycle.py) · the `agents.create` call · [The Three Resources](readme.md#the-three-resources)
**Say:** The split is by lifetime: what stays the same across runs lives on the Agent, what varies per run lives on the Session. A configuration you can point at is a configuration you can pin.

```python
    agent = client.beta.agents.create(
        name=f"lifecycle-explorer-{suffix}",
        model="claude-sonnet-5",
        system="You are a concise assistant. Answer in one short paragraph.",
        tools=[{"type": "agent_toolset_20260401"}],
    )
```

**Result:** [`session-lifecycle-solution/01-session-lifecycle.py`](session-lifecycle-solution/01-session-lifecycle.py) opens the Session with a pointer and nothing else: no `model`, no `system`, no `tools`

```python
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment.id,
    title="Session lifecycle walkthrough",
)
```

**Gotcha:** anyone arriving from the Messages API expects the model per turn, so name the absence out loud.

### Beat 2: two states carry the whole machine, and `idle` is ambiguous (1.5 min)

**Open:** [`session-lifecycle/lifecycle.py`](session-lifecycle/lifecycle.py) · the polling loop · [Session as a State Machine](readme.md#session-as-a-state-machine)
**Say:** A Session is a state machine you observe from outside as it moves between states. `idle` only says nobody is working right now, and a finished turn and a blocked turn both read that way.

```python
while True:
    current = client.beta.sessions.retrieve(session.id)
    if current.status != last_status:
        print(f"status -> {current.status}")
        last_status = current.status
    log = list(client.beta.sessions.events.list(session.id, order="asc"))
    idle = [e for e in log if e.type == "session.status_idle"]
    if current.status == "terminated" or any(
        e.stop_reason.type != "requires_action" for e in idle
    ):
        break
    time.sleep(2)
```

**Result:** [`session-lifecycle-solution/01-session-lifecycle.py`](session-lifecycle-solution/01-session-lifecycle.py) stamps every transition with elapsed seconds

```diff
+started = time.monotonic()
 last_status = None
...
-        print(f"status -> {current.status}")
+        print(f"{time.monotonic() - started:6.1f}s  status -> {current.status}")
```

**Gotcha:** breaking on `idle` is honest only because this demo asks one question with no gate; `rescheduling` follows a retryable error and `terminated` is irreversible.

### Beat 3: the event log is a queryable timeline (1.5 min)

**Open:** [`session-lifecycle/lifecycle.py`](session-lifecycle/lifecycle.py) · the `events.list` loop
**Say:** Every persisted event outlives the process that produced it, so history can be queried after the fact. That turns a dropped connection into a minor inconvenience.

```python
print("\nevent log")
for event in log:
    print(f"  {event.type}")
```

**Result:** [`session-lifecycle-solution/01-session-lifecycle.py`](session-lifecycle-solution/01-session-lifecycle.py) decodes payloads off that same log and reads `usage` off the finished Session

```python
print("\nevent log")
for event in log:
    if event.type == "agent.message":
        text = "".join(block.text for block in event.content)
        print(f"  {event.type:32} {text}")
    elif event.type == "agent.tool_use":
        print(f"  {event.type:32} {event.name} {event.input}")
    elif event.type == "session.status_idle":
        print(f"  {event.type:32} stop_reason={event.stop_reason.type}")
    else:
        print(f"  {event.type}")

usage = client.beta.sessions.retrieve(session.id).usage
print(f"\nusage {usage}")
```

**Gotcha:** the `user.message` the script sent appears in this log beside the agent's replies, because both sides write to one shared timeline.

## If the room asks

| Question | Answer |
|---|---|
| The Session sits at `running` far longer than expected. | Open the Console trace URL the script printed; it replays the same events with span timings and shows a stuck tool call. |
| Why poll when there is a stream? | Polling makes the state machine visible one transition at a time. |
