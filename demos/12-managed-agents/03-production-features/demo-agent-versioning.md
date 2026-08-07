# Ship an Agent Version Behind a Permission Gate

You publish two versions, gate `bash` on the second, run a Session pinned to each, and answer the confirmation the gated run parks on. Plan for 15 minutes; you finish with a version list proving nothing was overwritten and a gated run that only proceeds once you allow it.

------

Run it from [`agent-versioning/`](agent-versioning/readme.md). The completed reference is [`agent-versioning-solution/`](agent-versioning-solution/versioning.py).

## Step 1: Publish Version One

```python
agent = client.beta.agents.create(
    name=f"release-auditor-{suffix}",
    model="claude-sonnet-5",
    system="You inspect the container and report findings in one line.",
    tools=[{"type": "agent_toolset_20260401"}],
)
v1 = agent.version
```

**Expected result:** `version  1  (bash runs unattended)`. Versions count up per Agent, starting at `1`, and the number is only meaningful next to its Agent ID.

## Step 2: Publish Version Two With a Gate on Bash

```python
gated = client.beta.agents.update(
    agent.id,
    version=v1,
    tools=[{
        "type": "agent_toolset_20260401",
        "default_config": {"permission_policy": {"type": "always_allow"}},
        "configs": [{"name": "bash", "permission_policy": {"type": "always_ask"}}],
    }],
)
v2 = gated.version
```

**Expected result:** `version  2  (bash requires confirmation)`. The `version=v1` argument is an optimistic lock: it says "I am editing the version I last read". Two operators racing on the same Agent means the second update fails rather than silently clobbering the first.

Note the shape. There is no top-level `permissions` block on an Agent. Policies attach per tool inside the toolset, `default_config` sets the baseline, and `configs` overrides individual tools by name.

## Step 3: List the Published Versions

```python
for version in client.beta.agents.versions.list(agent.id):
    print(version.version, version.updated_at)
```

**Expected result:** both versions, newest first. Nothing was overwritten.

## Step 4: Run a Session Pinned to Version One

```python
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": v1},
    environment_id=environment.id,
)
```

With the prompt `Run \`uname -a\` and report the kernel.`

**Expected result:** the stream shows `agent.tool_use` with `permission=allow`, the command runs unattended, and the Session reaches `end_turn`. The gate published in step 2 has no effect here, because this Session is pinned to the version that predates it. That is the point: existing Sessions do not migrate.

## Step 5: Run a Session on the Latest Version

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
)
```

Passing the bare Agent ID resolves to the newest version.

**Expected result:** the same prompt now produces `agent.tool_use` with `permission=ask`, and the Session goes idle with `stop_reason` of `requires_action`. Nothing has run. The platform paused the call before executing it and is waiting for a verdict.

## Step 6: Return the Verdict

The blocking event IDs come off the stop reason.

```python
for blocked_id in event.stop_reason.event_ids:
    client.beta.sessions.events.send(
        session.id,
        events=[{
            "type": "user.tool_confirmation",
            "tool_use_id": blocked_id,
            "result": "allow",
        }],
    )
```

**Expected result:** the Session returns to `running`, `uname -a` executes, and the agent reports the kernel. Re-run with `result` set to `deny` and an optional `deny_message`; the agent receives the rejection as feedback and adapts rather than crashing.

The identifier is worth calling out. `tool_use_id` is the ID of the `agent.tool_use` **event** (a `sevt_` value), not a `toolu_` block ID from the Messages API. Resolving only some of the blocked events re-emits `session.status_idle` with the remainder.

## Common Failures

| Symptom | Cause |
|---|---|
| `update` returns a conflict | Stale `version` argument; retrieve the Agent and retry |
| The gate never fires | Session pinned to a version published before the policy |
| Confirmation is rejected | Sent a `toolu_` block ID instead of the `sevt_` event ID |
| Session idles again after approval | Only some of `stop_reason.event_ids` were resolved |
