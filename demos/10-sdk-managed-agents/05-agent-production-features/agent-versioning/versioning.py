from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = Anthropic()
suffix = uuid4().hex[:8]

agent = client.beta.agents.create(
    name=f"release-auditor-{suffix}",
    model="claude-sonnet-5",
    system="You inspect the container and report findings in one line.",
    tools=[{"type": "agent_toolset_20260401"}],
)
print(f"agent    {agent.id}")
print(f"version  {agent.version}  (bash runs unattended)\n")

environment = client.beta.environments.create(
    name=f"release-auditor-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)

session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": agent.version},
    environment_id=environment.id,
    title=f"Pinned to version {agent.version}",
)
print(f"session  {session.id}")
print(f"trace    https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {"type": "text", "text": "Run `uname -a` and report the kernel."}
                ],
            }
        ],
    )
    for event in stream:
        if event.type == "agent.message":
            print("".join(block.text for block in event.content))
        elif event.type == "agent.tool_use":
            print(f"[tool] {event.name} permission={event.evaluated_permission}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
print(f"\nAgent {agent.id} stays published at version {agent.version}.")
