# Add an Approval Gate to a Managed Agent

A custom tool has no implementation on Anthropic's side, so the Agent hands the call to your application, the Session parks, and nothing proceeds until you answer. You declare a fake `send_invoice_email` (recognizably sensitive without needing a real integration), run to the gate, capture the pending call as it streams past, and resume the Session with an allow and then a deny.

------

Run it from [`approval-gate/`](approval-gate/readme.md). The completed reference is [`approval-gate-solution/`](approval-gate-solution/demo.py).

## Step 1: Declare the Custom Tool

`SEND_INVOICE_EMAIL` in [`approval-gate/demo.py`](approval-gate/demo.py) is a `"type": "custom"` tool with a name, a description and an `input_schema` requiring `to`, `subject` and `body`. Add it to the Agent:

```python
agent = client.beta.agents.create(
    name=f"invoice-drafter-{suffix}",
    model="claude-sonnet-5",
    system="You draft and send invoice emails. Always send once the draft is ready.",
    tools=[{"type": "agent_toolset_20260401"}, SEND_INVOICE_EMAIL],
)
```

**Expected result:** an `agent_` identifier. Custom tools sit in the same `tools` array as the built-in toolset. There is no permission policy on a custom tool and none is needed, because you are the one executing it.

## Step 2: Run to the Gate

The invoice facts in this prompt are load bearing: without a number, amount or due date the agent asks for them, ends the turn at `end_turn`, and the gate never fires.

```text
Draft the Q1 invoice email to acme@example.com for invoice INV-2026-Q1,
42,000 EUR for the Q1 platform subscription, due 2026-04-30, and send it.
Do not ask for further details or confirmation.
```

```text
[pending] sevt_01Vw5xxXT39LDyMnuD9tt6nm send_invoice_email
  body: Dear Acme Team,
...
  subject: Invoice INV-2026-Q1 - Q1 Platform Subscription
  to: acme@example.com
[idle] stop_reason=requires_action
```

The stop reason names the blocking events, but the arguments live on the earlier `agent.custom_tool_use` event, so keep a lookup as you stream:

```python
elif event.type == "agent.custom_tool_use":
    pending[event.id] = event
```

**Expected result:** by the time `requires_action` arrives, every ID in `stop_reason.event_ids` is a key in `pending`. The container is checkpointed and the Session will still be there tomorrow.

## Step 3: Return the Result

Answer each blocked call with a `user.custom_tool_result` keyed by `custom_tool_use_id`. A refusal is the same event with `is_error` set and a reason:

```python
results.append({
    "type": "user.custom_tool_result",
    "custom_tool_use_id": blocked_id,
    "is_error": True,
    "content": [{
        "type": "text",
        "text": "Operator denied the send. Do not retry; summarize the draft instead.",
    }],
})
```

**Expected result:** on an allow the Session returns to `running` and the agent confirms the send; on this deny it drops the send and does what the message told it to do. Sending `tool_use_id` in place of `custom_tool_use_id` is a 400.
