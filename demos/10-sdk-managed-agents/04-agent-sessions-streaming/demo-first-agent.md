# Build a Managed Agent End to End

One flow touches every primitive so the API surface becomes muscle memory: upload a file, mount it on the Session, open the stream before sending, then clean up. You build a CSV analyst against a real sales fixture and pull the artifact it writes back out of the container.

------

Run it from [`csv-analyst/`](csv-analyst/readme.md). The completed reference is [`csv-analyst-solution/`](csv-analyst-solution/01-analyze-csv.py).

## Step 1: Create the Environment and Mount the File on the Session

Files are uploaded once and referenced by ID, so upload `sales.csv` with `client.beta.files.upload`, create the Agent and the Environment, and mount the file on the Session:

```python
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment.id,
    resources=[{
        "type": "file",
        "file_id": upload.id,
        "mount_path": "/mnt/session/uploads/sales.csv",
    }],
)
```

**Expected result:** an `sesn_` identifier, and the create call blocks until the mount is in place. `mount_path` must be absolute, and parent directories are created for you.

## Step 2: Stream First, Then Send

Open the stream before you send the prompt below, and break out of the event loop only on a terminal stop reason:

```python
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
    for event in stream:
        ...
```

```text
Analyze /mnt/session/uploads/sales.csv and write
/mnt/session/outputs/summary.md with the top 3 insights.
```

```python
elif event.type == "session.status_idle":
    if event.stop_reason.type != "requires_action":
        break
```

**Expected result:** events arrive in order, from `session.status_running` through the `bash` and `write` tool calls to `session.status_idle` with `stop_reason` of `end_turn`, and the loop exits once. A Session goes idle transiently whenever it needs something from you, and `requires_action` means exactly that: handle it and keep reading.

## Step 3: Collect What the Agent Wrote

Anything the agent writes under `/mnt/session/outputs/` is captured by the Files API and can be pulled back out.

```python
outputs = [
    metadata
    for metadata in client.beta.files.list(
        scope_id=session.id,
        betas=["managed-agents-2026-04-01"],
    )
    if metadata.downloadable
]
for metadata in outputs:
    client.beta.files.download(metadata.id).write_to_file(output_dir / metadata.filename)
```

**Expected result:** `[downloaded] outputs/summary.md  (1843 bytes)`. The `downloadable` filter is not optional: the Session scope also lists the file you mounted as an input, and that copy comes back `downloadable=False`, so an unfiltered loop fails with `400 File '...' is not downloadable`.
