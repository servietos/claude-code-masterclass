---
presents: demo-agent-versioning.md
budget: 4 min
beats: 4
---

# Present: Ship an Agent Version Behind a Permission Gate

An Agent version behaves like a container image tag: `update` publishes rather than mutates. Four beats: the publish, the per-tool permission policy, a Session pinned to the older version, and the reply that releases a gated call.

------

## Beats

### Beat 1: update publishes, it never mutates (1 min)

**Open:** [`agent-versioning/versioning.py`](agent-versioning/versioning.py) · it only ever calls `agents.create` · [Versioning Agents as Deployable Units](readme.md#versioning-agents-as-deployable-units)
**Say:** Agent configuration is a released artifact, so `update` publishes another one and leaves the old one standing. Nothing that has already run can be edited out from under you.

```python
gated = client.beta.agents.update(
    agent.id,
    version=v1,
    tools=[
...
)
v2 = gated.version
```

**Result:** [`agent-versioning-solution/versioning.py`](agent-versioning-solution/versioning.py) lists what `update` left standing

```python
print("published versions")
for version in client.beta.agents.versions.list(agent.id):
    print(f"  {version.version}  {version.updated_at}")
```

**Gotcha:** `version=v1` is an optimistic lock, so a conflict is not a bug: retrieve the Agent and retry.

### Beat 2: policies attach per tool inside the toolset, not to the Agent (1 min)

**Open:** [`agent-versioning/versioning.py`](agent-versioning/versioning.py) · its toolset has no `default_config` and no `configs` · [Permission Policies and Tool Confirmation](readme.md#permission-policies-and-tool-confirmation)
**Say:** Permission is a property of a capability, not of the agent holding it, so the policy sits beside the tool it governs. One toolset stays permissive while a single dangerous tool stops for a human.

```python
        {
            "type": "agent_toolset_20260401",
            "default_config": {"permission_policy": {"type": "always_allow"}},
            "configs": [{"name": "bash", "permission_policy": {"type": "always_ask"}}],
        }
```

**Result:** [`agent-versioning-solution/versioning.py`](agent-versioning-solution/versioning.py) publishes the same toolset twice, once open and once with `bash` gated

```python
print(f"version  {v1}  (bash runs unattended)")
...
print(f"version  {v2}  (bash requires confirmation)\n")
```

**Gotcha:** there is no top-level `permissions` block on an Agent, which is the shape people guess and then cannot find in the docs.

### Beat 3: Sessions pin to a version, they do not migrate (1 min)

**Open:** [`agent-versioning/versioning.py`](agent-versioning/versioning.py) · one inline Session, opened before any gate exists
**Say:** Work already in flight does not change its mind halfway, so a run keeps the rules it started under. Publishing is not deploying: traffic moves only as new Sessions are created.

```python
def run(agent_ref, title):
    session = client.beta.sessions.create(
        agent=agent_ref,
        environment_id=environment.id,
        title=title,
    )
```

**Result:** [`agent-versioning-solution/versioning.py`](agent-versioning-solution/versioning.py) turns one inline Session into two pinned runs against one Environment

```diff
+run({"type": "agent", "id": agent.id, "version": v1}, f"Pinned to version {v1}")
+run(agent.id, f"Latest version {v2}")
 
-client.beta.sessions.delete(session.id)
 client.beta.environments.delete(environment.id)
-print(f"\nAgent {agent.id} stays published at version {agent.version}.")
+print(f"\nAgent {agent.id} keeps both versions. Sessions pin, they do not migrate.")
```

**Gotcha:** same prompt, same Environment, both times; the only variable is the version reference, and the bare Agent ID resolves to the newest.

### Beat 4: the confirmation is keyed by the event ID, and partial answers re-idle (1 min)

**Open:** [`agent-versioning/versioning.py`](agent-versioning/versioning.py) · its idle branch prints the stop reason and stops · [Two Gates, Not One](../05-human-in-the-loop/readme.md#two-gates-not-one)
**Say:** A gate is a paused call waiting on a verdict, and the verdict travels back as another event on the same timeline. One pause can hold several blocked calls, so the answer has to name which call it answers.

```python
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break
```

**Result:** the reply loop exists only in [`agent-versioning-solution/versioning.py`](agent-versioning-solution/versioning.py)

```python
                for blocked_id in event.stop_reason.event_ids:
                    print(f"[gate] approving {blocked_id}")
                    client.beta.sessions.events.send(
...
                                "type": "user.tool_confirmation",
                                "tool_use_id": blocked_id,
                                "result": "allow",
```

**Gotcha:** `tool_use_id` here is the `sevt_` ID of the `agent.tool_use` event, not a `toolu_` block ID from the Messages API.

## If the room asks

| Question | Answer |
|---|---|
| The gate never fired. Is the policy wrong? | Probably not: the Session is pinned to a version published before the policy, so it never sees it. |
| The Session idled again right after I approved. | Only part of `stop_reason.event_ids` was resolved; answer all of them. |
| Can I deny instead of allowing? | Yes, `result` takes `deny` with an optional `deny_message`, and the agent adapts rather than crashing. |
| How does this look in production, without a human at a terminal? | A webhook on `session.status_idled` notifies a reviewer and your backend posts the confirmation; the payload is thin and HMAC signed, so the handler fetches the Session for state. |
