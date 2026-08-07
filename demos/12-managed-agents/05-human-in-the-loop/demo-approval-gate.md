# Add an Approval Gate to a Managed Agent

A custom tool has no implementation on Anthropic's side, so the Agent hands the call to your application, the Session parks, and nothing proceeds until you answer. You declare a fake `send_invoice_email` (recognizably sensitive without needing a real integration), run to the gate, capture the pending call as it streams past, and resume the Session with an allow and then a deny. Plan for 20 minutes; you finish able to tell this handoff apart from the permission-policy gate.

------

Run it from [`approval-gate/`](approval-gate/readme.md). The completed reference is [`approval-gate-solution/`](approval-gate-solution/demo.py).

## Step 1: Declare the Custom Tool

```python
SEND_INVOICE_EMAIL = {
    "type": "custom",
    "name": "send_invoice_email",
    "description": "Sends a drafted invoice email to a customer.",
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient address"},
            "subject": {"type": "string", "description": "Email subject line"},
            "body": {"type": "string", "description": "Plain-text email body"},
        },
        "required": ["to", "subject", "body"],
    },
}

agent = client.beta.agents.create(
    name=f"invoice-drafter-{suffix}",
    model="claude-sonnet-5",
    system="You draft and send invoice emails. Always send once the draft is ready.",
    tools=[{"type": "agent_toolset_20260401"}, SEND_INVOICE_EMAIL],
)
```

**Expected result:** an `agent_` identifier. Custom tools sit in the same `tools` array as the built-in toolset. There is no permission policy on a custom tool and none is needed, because you are the one executing it.

## Step 2: Run to the Gate

With this prompt:

```text
Draft the Q1 invoice email to acme@example.com for invoice INV-2026-Q1,
42,000 EUR for the Q1 platform subscription, due 2026-04-30, and send it.
Do not ask for further details or confirmation.
```

**Expected result:** the agent drafts the body, then the stream carries `agent.custom_tool_use` with the tool name and the full argument object, followed by `session.status_idle` with `stop_reason` of `requires_action`. Print the arguments on screen; seeing the drafted subject and body is what makes the gate feel real rather than theoretical.

```text
[pending] sevt_01Vw5xxXT39LDyMnuD9tt6nm send_invoice_email
  body: Dear Acme Team,
...
  subject: Invoice INV-2026-Q1 - Q1 Platform Subscription
  to: acme@example.com
[idle] stop_reason=requires_action
```

The invoice facts in the prompt are load bearing. Ask for "the Q1 invoice" with no number, amount or due date and the agent does the sensible thing: it asks you for them and ends the turn at `end_turn`, so the tool is never called and the gate never fires.

The starter stops here on purpose. Pause and ask the room what the platform is doing right now: nothing, at zero cost, for as long as it takes. The container is checkpointed and the Session will still be there tomorrow.

## Step 3: Capture the Pending Call

The stop reason names the blocking events, but the arguments live on the earlier `agent.custom_tool_use` event, so keep a lookup as you stream.

```python
elif event.type == "agent.custom_tool_use":
    pending[event.id] = event
```

**Expected result:** by the time `requires_action` arrives, every ID in `stop_reason.event_ids` is a key in `pending`. This is the small piece of bookkeeping every real client ends up writing.

## Step 4: Return the Result

```python
results.append({
    "type": "user.custom_tool_result",
    "custom_tool_use_id": blocked_id,
    "content": [{"type": "text", "text": f"Delivered to {call.input['to']}."}],
})
client.beta.sessions.events.send(session.id, events=results)
```

**Expected result:** the Session returns to `running` and the agent confirms the send. Note the field name: `custom_tool_use_id`, not `tool_use_id`. The two event types take different keys, and mixing them is a 400.

## Step 5: Show the Deny Path

A refusal is feedback, not a failure. Send the result with `is_error` set and say why.

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

**Expected result:** the agent reads the rejection, drops the send, and does what the message told it to do instead. Run the demo twice, once each way.

## Stretch: Make the Gate Asynchronous

The demo blocks on `input()`, which is fine on a projector and wrong in production. Nothing in the Session requires your process to stay alive: the Session is already idle and checkpointed. Swap the prompt for a webhook subscription on `session.status_idled`, persist the blocking event ID, notify a reviewer through whatever channel they already read, and post the `user.custom_tool_result` when the verdict comes back hours later.

## Common Failures

| Symptom | Cause |
|---|---|
| 400 on the result event | Used `tool_use_id` instead of `custom_tool_use_id` |
| `KeyError` on the pending lookup | Did not record `agent.custom_tool_use` while streaming |
| The agent retries the denied call | Deny text did not say what to do instead |
| The run ends at `end_turn` with nothing pending | The prompt named no invoice number, amount or due date, so the agent asked for them instead of calling the tool |
| The loop hangs after sending the result | Broke out of the stream before the follow-up turn arrived |
