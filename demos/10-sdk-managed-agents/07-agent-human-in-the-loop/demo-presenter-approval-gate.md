---
presents: demo-approval-gate.md
budget: 4 min
beats: 4
---

# Present: Add an Approval Gate to a Managed Agent

A custom tool is a declaration with no server-side implementation, which is what separates it from a permission policy. Four beats: that distinction, the parked Session that costs nothing, capturing the pending call from the stream, and resuming with an allow or a deny.

------

## Beats

### Beat 1: a custom tool is a declaration with no implementation on Anthropic's side (1 min)

**Open:** [`approval-gate/demo.py`](approval-gate/demo.py) · the `SEND_INVOICE_EMAIL` declaration · [Two Gates, Not One](readme.md#two-gates-not-one)
**Say:** Declaring a tool states what the agent may ask for and leaves the execution to your application. Keeping the sensitive action outside the sandbox keeps the credentials, the audit trail and the final decision in systems you already run.

```python
SEND_INVOICE_EMAIL = {
    "type": "custom",
    "name": "send_invoice_email",
    "description": "Sends a drafted invoice email to a customer.",
    "input_schema": {
...
        "required": ["to", "subject", "body"],
    },
}
```

**Result:** [`approval-gate-solution/01-approval-gate.py`](approval-gate-solution/01-approval-gate.py) carries the declaration unchanged, in the same `tools` array as the built-in toolset and with no `permission_policy` key

```python
agent = client.beta.agents.create(
    name=f"invoice-drafter-{suffix}",
    model="claude-sonnet-5",
    system="You draft and send invoice emails. Always send once the draft is ready.",
    tools=[{"type": "agent_toolset_20260401"}, SEND_INVOICE_EMAIL],
)
```

**Gotcha:** a permission policy gates a tool the platform runs and you answer with `user.tool_confirmation`; a custom tool has none and you answer with `user.custom_tool_result`.

### Beat 2: the Session parks, and parking is free (1 min)

**Open:** [`approval-gate/demo.py`](approval-gate/demo.py) · the `agent.custom_tool_use` and `session.status_idle` branches · [Why HITL Sells the Module](readme.md#why-hitl-sells-the-module)
**Say:** A human in the loop puts an unbounded wait in the middle of a program, and holding that wait open is what usually makes approval flows expensive. Here it is a checkpointed state, and no connection is held open.

```python
        elif event.type == "agent.custom_tool_use":
            print(f"[pending] {event.id} {event.name}")
            for key, value in event.input.items():
                print(f"  {key}: {value}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            break
```

**Result:** the starter run ends at the gate, which its final line says out loud (no file is written)

```python
print("\nThe session stopped at the gate. The solution folder resumes it.")
```

**Gotcha:** read the drafted subject and body off the screen; a pause of one minute and a pause of one week cost the same.

### Beat 3: the stop reason names the blocked calls, the earlier event holds their arguments (1 min)

**Open:** [`approval-gate/demo.py`](approval-gate/demo.py) · it prints the pending call and never records it
**Say:** No single event carries everything a decision needs: the identity of a blocked call and its arguments arrive separately. Consuming an event-sourced protocol means accumulating as you read.

```python
            results = []
            for blocked_id in event.stop_reason.event_ids:
                call = pending[blocked_id]
                verdict = input(f"  Approve {call.name}? [y/n] ").strip().lower()
```

**Result:** two added lines are the whole of the bookkeeping in [`approval-gate-solution/01-approval-gate.py`](approval-gate-solution/01-approval-gate.py)

```diff
+pending = {}
...
         elif event.type == "agent.custom_tool_use":
+            pending[event.id] = event
             print(f"[pending] {event.id} {event.name}")
```

**Gotcha:** `stop_reason.event_ids` gives IDs and nothing else, so a client that did not keep the event has nothing to act on.

### Beat 4: a deny is feedback the agent reads (1 min)

**Open:** [`approval-gate/demo.py`](approval-gate/demo.py) · it breaks at idle and sends nothing back · [Permission Policies and Tool Confirmation](../05-agent-production-features/readme.md#permission-policies-and-tool-confirmation)
**Say:** A refusal is an input to the agent's reasoning, and the run continues after it, so what you write into it is a prompt. A bare no leaves the model guessing whether to retry or abandon the task.

```python
                    results.append(
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": blocked_id,
                            "is_error": True,
...
                                    "text": "Operator denied the send. Do not retry; summarize the draft instead.",
                                }
```

**Result:** [`approval-gate-solution/01-approval-gate.py`](approval-gate-solution/01-approval-gate.py) builds allow and deny in one branch and returns every verdict in a single `events.send`

```diff
         elif event.type == "session.status_idle":
             print(f"[idle] stop_reason={event.stop_reason.type}")
-            break
+            if event.stop_reason.type != "requires_action":
+                break
+
+            results = []
```

**Gotcha:** the field is `custom_tool_use_id`; the two event types take different keys, and mixing them is a 400.

## If the room asks

| Question | Answer |
|---|---|
| I get a 400 on the result event. | `tool_use_id` was used where `custom_tool_use_id` belongs. |
| `KeyError` on the pending lookup. | The `agent.custom_tool_use` event was not recorded while streaming, so its arguments were never kept. |
| The loop hangs after I send the result. | The stream was broken out of before the follow-up turn arrived; keep reading until a terminal stop reason. |
