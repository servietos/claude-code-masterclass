import time

from common import client, here, record_run, send_task, suffix, text_of, watch

TASK = (
    "Search Microsoft Learn for what Azure Container Apps bills for. "
    "Then use the docx skill to write "
    "/mnt/session/outputs/container-apps-brief.docx with a heading, "
    "three bullet findings, and the doc URLs you used."
)

environment = client.beta.environments.create(
    name=f"docs-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "limited", "allow_mcp_servers": True}},
)
print(f"environment  {environment.id}")

agent = client.beta.agents.create(
    name=f"docs-extended-{suffix}",
    model="claude-sonnet-5",
    system="You research Microsoft documentation and turn the findings into a document.",
    mcp_servers=[
        {
            "type": "url",
            "name": "microsoft-learn",
            "url": "https://learn.microsoft.com/api/mcp",
        }
    ],
    skills=[{"type": "anthropic", "skill_id": "docx"}],
    tools=[
        {"type": "agent_toolset_20260401"},
        {"type": "mcp_toolset", "mcp_server_name": "microsoft-learn"},
    ],
)
print(f"agent        {agent.id}  version={agent.version}")

session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Gated turn",
)
record_run(session.id, environment.id)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")


def show(event):
    if event.type == "agent.mcp_tool_use":
        print(f"  mcp_tool_use  {event.name} permission={getattr(event, 'evaluated_permission', None)}")
    elif event.type == "agent.mcp_tool_result":
        print("  mcp_tool_result")
    elif event.type == "session.status_idle":
        print(f"  status_idle   stop_reason={event.stop_reason.type}")
        if event.stop_reason.type == "requires_action":
            print(f"  waiting on    {event.stop_reason.event_ids}")


send_task(session.id, TASK)
watch(session.id, show, stop_on_requires_action=True)
print(f"status       {client.beta.sessions.retrieve(session.id).status}")
