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
        {
            "type": "mcp_toolset",
            "mcp_server_name": "microsoft-learn",
            "default_config": {"permission_policy": {"type": "always_allow"}},
        },
    ],
)
print(f"agent        {agent.id}  version={agent.version}")

session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Extended turn",
)
record_run(session.id, environment.id)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")


def show(event):
    if event.type == "agent.tool_use":
        print(f"  tool_use      {event.name} {str(event.input)[:70]}")
    elif event.type == "agent.mcp_tool_use":
        print(f"  mcp_tool_use  {event.name} {event.input}")
    elif event.type == "agent.message":
        print(f"  message       {text_of(event.content)[:200]}")
    elif event.type == "session.status_idle":
        print(f"  status_idle   stop_reason={event.stop_reason.type}")


send_task(session.id, TASK)
watch(session.id, show)

output_dir = here / "outputs"
output_dir.mkdir(exist_ok=True)
outputs = []
for attempt in range(5):
    outputs = [
        metadata
        for metadata in client.beta.files.list(scope_id=session.id, betas=["managed-agents-2026-04-01"])
        if metadata.downloadable
    ]
    if outputs:
        break
    time.sleep(2)

for metadata in outputs:
    client.files.download(metadata.id).write_to_file(output_dir / metadata.filename)
    print(f"[downloaded] outputs/{metadata.filename}  ({metadata.size_bytes} bytes)")
