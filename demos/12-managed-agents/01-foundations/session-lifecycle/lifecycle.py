import os
import time
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = Anthropic()
suffix = uuid4().hex[:8]

agent_id = os.environ.get("MANAGED_AGENT_ID")
if not agent_id:
    agent = client.beta.agents.create(
        name=f"lifecycle-explorer-{suffix}",
        model="claude-sonnet-5",
        system="You are a concise assistant. Answer in one short paragraph.",
        tools=[{"type": "agent_toolset_20260401"}],
    )
    agent_id = agent.id
    print(f"agent        {agent_id}  (export MANAGED_AGENT_ID={agent_id} to reuse)")
else:
    print(f"agent        {agent_id}  (reused)")

environment = client.beta.environments.create(
    name=f"lifecycle-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)
print(f"environment  {environment.id}")

session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment.id,
    title="Session lifecycle walkthrough",
)
print(f"session      {session.id}  status={session.status}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

client.beta.sessions.events.send(
    session.id,
    events=[
        {
            "type": "user.message",
            "content": [
                {
                    "type": "text",
                    "text": "Compare Claude Code to Claude Cowork",
                }
            ],
        }
    ],
)

last_status = None
while True:
    current = client.beta.sessions.retrieve(session.id)
    if current.status != last_status:
        print(f"status -> {current.status}")
        last_status = current.status
    log = list(client.beta.sessions.events.list(session.id, order="asc"))
    idle = [e for e in log if e.type == "session.status_idle"]
    if current.status == "terminated" or any(
        e.stop_reason.type != "requires_action" for e in idle
    ):
        break
    time.sleep(2)

print("\nevent log")
for event in log:
    print(f"  {event.type}")

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
print("\nDeleted the session and the environment. The agent stays reusable.")
