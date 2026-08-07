from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = Anthropic()
suffix = uuid4().hex[:8]

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
print(f"agent        {agent.id}")

environment = client.beta.environments.create(
    name=f"invoice-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)

session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Invoice approval gate",
)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

prompt = (
    "Draft the Q1 invoice email to acme@example.com for invoice INV-2026-Q1, "
    "42,000 EUR for the Q1 platform subscription, due 2026-04-30, and send it. "
    "Do not ask for further details or confirmation."
)
pending = {}

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
    for event in stream:
        if event.type == "agent.message":
            print("".join(block.text for block in event.content))
        elif event.type == "agent.custom_tool_use":
            pending[event.id] = event
            print(f"[pending] {event.id} {event.name}")
            for key, value in event.input.items():
                print(f"  {key}: {value}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

            results = []
            for blocked_id in event.stop_reason.event_ids:
                call = pending[blocked_id]
                verdict = input(f"  Approve {call.name}? [y/n] ").strip().lower()
                if verdict == "y":
                    results.append(
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": blocked_id,
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Delivered to {call.input['to']}.",
                                }
                            ],
                        }
                    )
                else:
                    results.append(
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": blocked_id,
                            "is_error": True,
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Operator denied the send. Do not retry; summarize the draft instead.",
                                }
                            ],
                        }
                    )
                print(f"  verdict: {'allow' if verdict == 'y' else 'deny'}")

            client.beta.sessions.events.send(session.id, events=results)

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
print("\nDeleted the session and the environment.")
