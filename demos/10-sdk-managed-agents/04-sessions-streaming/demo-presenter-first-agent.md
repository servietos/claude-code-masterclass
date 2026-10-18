---
presents: demo-first-agent.md
budget: 4 min
beats: 4
---

# Present: Build a Managed Agent End to End

Three ordering rules and one retrieval: the mount belongs to the Session, the stream opens before the message is sent, the loop exits on a stop reason. Four beats close on pulling the file the agent wrote back out of the container.

------

## Beats

### Beat 1: the mount belongs to the Session, because the Environment is a template (1 min)

**Open:** [`csv-analyst/demo.py`](csv-analyst/demo.py) · the `resources` block on `sessions.create` · [`csv-analyst/sales.csv`](csv-analyst/sales.csv)
**Say:** An Environment is a template many Sessions instantiate at once, so per-run data belongs to the run. Attach a customer's file to the template and the template stops being reusable.

```python
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment.id,
...
            "type": "file",
            "file_id": upload.id,
            "mount_path": "/mnt/session/uploads/sales.csv",
        }
    ],
)
```

**Result:** the mount path is what the prompt addresses, unchanged in [`csv-analyst-solution/demo.py`](csv-analyst-solution/demo.py)

```python
prompt = (
    "Analyze /mnt/session/uploads/sales.csv and write "
    "/mnt/session/outputs/summary.md with the top 3 insights."
)
```

**Gotcha:** `mount_path` must be absolute, and the create call blocks until the mount is in place.

### Beat 2: open the stream before you send, because SSE has no replay (1 min)

**Open:** [`csv-analyst/demo.py`](csv-analyst/demo.py) · the `stream` context manager wrapping `events.send` · [Event-Based Communication Over SSE](readme.md#event-based-communication-over-sse)
**Say:** An SSE stream is a live subscription, so it delivers only what happens after you attach. The order of these two calls decides whether the first events arrive.

```python
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
```

**Result:** [`csv-analyst-solution/demo.py`](csv-analyst-solution/demo.py) keeps the `send` inside the `with` and adds dedupe by event ID

```diff
+seen_event_ids = set()
 with client.beta.sessions.events.stream(session.id) as stream:
...
+        if event.id in seen_event_ids:
+            continue
+        seen_event_ids.add(event.id)
```

**Gotcha:** sending first makes the early events arrive in one buffered clump, which looks exactly like a slow platform.

### Beat 3: breaking on `session.status_idle` alone is the classic client bug (1 min)

**Open:** [`csv-analyst/demo.py`](csv-analyst/demo.py) · the `session.status_idle` branch · [Session as a State Machine](../03-foundations/readme.md#session-as-a-state-machine)
**Say:** The event says a transition happened; the stop reason says what it meant, and only the reason is safe to branch on. A Session idles every time it needs something from you.

```python
        elif event.type == "agent.tool_use":
            print(f"[tool] {event.name} {event.input}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break
```

**Result:** [`csv-analyst-solution/demo.py`](csv-analyst-solution/demo.py) adds one more branch to the same loop

```diff
         elif event.type == "agent.tool_use":
             print(f"[tool] {event.name} {event.input}")
+        elif event.type == "span.model_request_end":
+            print(f"[usage] {event.model_usage}")
         elif event.type == "session.status_terminated":
```

**Gotcha:** only `end_turn` and `retries_exhausted` are terminal, so a loop breaking on the event type falls apart the moment a gate exists.

### Beat 4: outputs come back through the Files API, after a short indexing lag (1 min)

**Open:** [`csv-analyst/demo.py`](csv-analyst/demo.py) · it ends at cleanup and retrieves nothing · [Step 3: Collect What the Agent Wrote](demo-first-agent.md#step-3-collect-what-the-agent-wrote)
**Say:** The container disappears with the Session, so anything the agent produced needs a defined way out. Write under `/mnt/session/outputs/` and the platform captures it under the Session's scope.

```python
    outputs = [
        metadata
        for metadata in client.beta.files.list(
            scope_id=session.id,
            betas=["managed-agents-2026-04-01"],
        )
        if metadata.downloadable
    ]
```

**Result:** the retry loop and the per-file download exist only in [`csv-analyst-solution/demo.py`](csv-analyst-solution/demo.py), which writes into a local `outputs/`

```python
    if outputs:
        break
    time.sleep(2)

for metadata in outputs:
    client.beta.files.download(metadata.id).write_to_file(output_dir / metadata.filename)
```

**Gotcha:** the explicit `betas` argument is the one place you pass the Managed Agents beta by hand, and the `downloadable` filter is what keeps the mounted input CSV, which the Session scope also lists, out of the download loop.

## If the room asks

| Question | Answer |
|---|---|
| The first few events arrived together and late. Why? | The message was sent before the stream was opened, so everything queued until the consumer attached. |
| `files.list` returned nothing. What did I miss? | Either it was called too soon after idle, or `betas` was omitted. |
| The agent cannot find the CSV. | `mount_path` was relative, or the mount was attached to the Environment, which is the wrong resource. |
