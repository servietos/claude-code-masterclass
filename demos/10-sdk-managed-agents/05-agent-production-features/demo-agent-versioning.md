# Ship an Agent Version Behind a Permission Gate

You publish two versions, gate `bash` on the second, run a Session pinned to each, and answer the confirmation the gated run parks on. Plan for 15 minutes; you finish with a version list proving nothing was overwritten and a gated run that only proceeds once you allow it.

------

Run it from [`agent-versioning/`](agent-versioning/readme.md). The completed reference is [`agent-versioning-solution/`](agent-versioning-solution/01-agent-versioning.py).

## Step 1: Publish Version Two With a Gate on Bash

Version one is a plain `agents.create` with the open toolset, printed as `version  1  (bash runs unattended)`. `update` publishes version two with `bash` gated:

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

**Expected result:** `version  2  (bash requires confirmation)`. The `version=v1` argument is an optimistic lock: it says "I am editing the version I last read". `client.beta.agents.versions.list(agent.id)` then returns both versions, newest first, so nothing was overwritten.

There is no top-level `permissions` block on an Agent. Policies attach per tool inside the toolset, `default_config` sets the baseline, and `configs` overrides individual tools by name.

## Step 2: Run a Session Pinned to Version One

Send the prompt ``Run `uname -a` and report the kernel.`` twice: once pinned to version one, once on the bare Agent ID, which resolves to the newest version.

```python
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": v1},
    environment_id=environment.id,
)
```

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
)
```

**Expected result:** the pinned run shows `agent.tool_use` with `permission=allow` and reaches `end_turn`, because existing Sessions do not migrate. The latest run produces `permission=ask` and goes idle with `stop_reason` of `requires_action`; nothing has run, because the platform paused the call before executing it.

## Step 3: Return the Verdict

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

**Expected result:** the Session returns to `running`, `uname -a` executes, and the agent reports the kernel. `tool_use_id` is the ID of the `agent.tool_use` **event** (a `sevt_` value), and resolving only some of the blocked events re-emits `session.status_idle` with the remainder.
