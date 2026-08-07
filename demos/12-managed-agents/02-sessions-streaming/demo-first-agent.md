# Build a Managed Agent End to End

One flow touches every primitive so the API surface becomes muscle memory: upload a file, mount it on the Session, open the stream before sending, steer the run mid-flight, then clean up. You build a CSV analyst against a real sales fixture and pull the artifact it writes back out of the container. Plan for 25 minutes including a Q&A buffer, and keep the Console trace view open beside the terminal.

------

Run it from [`csv-analyst/`](csv-analyst/readme.md). The completed reference is [`csv-analyst-solution/`](csv-analyst-solution/demo.py).

## Step 1: Upload the CSV

Files are uploaded once and referenced by ID, instead of being resent as a blob on every turn.

```python
with csv_path.open("rb") as handle:
    # the tuple is the multipart form the SDK expects: filename, open handle, content type
    upload = client.beta.files.upload(file=("sales.csv", handle, "text/csv"))
```

**Expected result:** a `file_` identifier. Nothing is mounted yet; the file is just parked in your workspace.

## Step 2: Create the Agent

```python
agent = client.beta.agents.create(
    name=f"csv-analyst-{suffix}",
    model="claude-sonnet-5",
    system="You are a senior data analyst. Be concise and quantitative.",
    tools=[{"type": "agent_toolset_20260401"}],
)
```

**Expected result:** an `agent_` identifier.

## Step 3: Create the Environment and Mount the File on the Session

```python
environment = client.beta.environments.create(
    name=f"csv-analyst-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)

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

## Step 4: Stream First, Then Send

```python
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
    for event in stream:
        ...
```

With this prompt:

```text
Analyze /mnt/session/uploads/sales.csv and write
/mnt/session/outputs/summary.md with the top 3 insights.
```

**Expected result:** events arrive in order. `session.status_running`, then `agent.tool_use` for the `bash` calls the agent uses to inspect and aggregate the CSV, then a `write` tool call for the summary, then `agent.message` blocks as the analysis lands, then `session.status_idle` with `stop_reason` of `end_turn`. Switch to the Console trace and show the same run rendered visually with span timings.

## Step 5: Break on the Right Condition

```python
elif event.type == "session.status_idle":
    if event.stop_reason.type != "requires_action":
        break
```

**Expected result:** the loop exits once, at the end of the turn. Breaking on `session.status_idle` alone is the single most common bug in Managed Agents clients. A Session goes idle transiently whenever it needs something from you, and `requires_action` means exactly that: handle it and keep reading. The other two stop reasons, `end_turn` and `retries_exhausted`, are both terminal.

## Step 6: Collect What the Agent Wrote

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

**Expected result:** `[downloaded] outputs/summary.md  (1843 bytes)`. Note the explicit `betas` argument: this is a Files endpoint taking a Managed Agents parameter, so the SDK adds the Files header for you and you supply the other one. There is a short indexing lag after `session.status_idle`, which is why the solution retries a few times before giving up.

The `downloadable` filter is not optional. The Session scope also lists the file you mounted as an input, and that copy comes back `downloadable=False`, so an unfiltered loop fails with `400 File '...' is not downloadable` before it ever reaches `summary.md`.

## Common Failures

| Symptom | Cause |
|---|---|
| The first few events arrive together, late | The message was sent before the stream was opened |
| The loop exits before the agent finishes | Breaking on `session.status_idle` without checking `stop_reason` |
| `files.list` returns nothing | Called too soon after idle, or `betas` was omitted |
| The agent cannot find the CSV | `mount_path` was relative, or the mount was put on the Environment |
