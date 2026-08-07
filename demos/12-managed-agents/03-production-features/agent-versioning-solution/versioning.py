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
v1 = agent.version
print(f"agent    {agent.id}")
print(f"version  {v1}  (bash runs unattended)")

gated = client.beta.agents.update(
    agent.id,
    version=v1,
    tools=[
        {
            "type": "agent_toolset_20260401",
            "default_config": {"permission_policy": {"type": "always_allow"}},
            "configs": [{"name": "bash", "permission_policy": {"type": "always_ask"}}],
        }
    ],
)
v2 = gated.version
print(f"version  {v2}  (bash requires confirmation)\n")

print("published versions")
for version in client.beta.agents.versions.list(agent.id):
    print(f"  {version.version}  {version.updated_at}")

environment = client.beta.environments.create(
    name=f"release-auditor-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)

prompt = "Run `uname -a` and report the kernel."


def run(agent_ref, title):
    session = client.beta.sessions.create(
        agent=agent_ref,
        environment_id=environment.id,
        title=title,
    )
    print(f"\n=== {title} ===")
    print(f"session  {session.id}")
    print(f"trace    https://platform.claude.com/workspaces/default/sessions/{session.id}")

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[
                {"type": "user.message", "content": [{"type": "text", "text": prompt}]}
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
                for blocked_id in event.stop_reason.event_ids:
                    print(f"[gate] approving {blocked_id}")
                    client.beta.sessions.events.send(
                        session.id,
                        events=[
                            {
                                "type": "user.tool_confirmation",
                                "tool_use_id": blocked_id,
                                "result": "allow",
                            }
                        ],
                    )

    client.beta.sessions.delete(session.id)


run({"type": "agent", "id": agent.id, "version": v1}, f"Pinned to version {v1}")
run(agent.id, f"Latest version {v2}")

client.beta.environments.delete(environment.id)
print(f"\nAgent {agent.id} keeps both versions. Sessions pin, they do not migrate.")
