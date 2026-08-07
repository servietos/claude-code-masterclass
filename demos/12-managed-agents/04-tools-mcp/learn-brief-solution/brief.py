import time
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = Anthropic()
suffix = uuid4().hex[:8]

agent = client.beta.agents.create(
    name=f"learn-researcher-{suffix}",
    model="claude-sonnet-5",
    system="You research Microsoft documentation and turn the findings into a document.",
    mcp_servers=[
        {
            "type": "url",
            "name": "microsoft-learn",
            "url": "https://learn.microsoft.com/api/mcp",
        }
    ],
    tools=[
        {"type": "agent_toolset_20260401"},
        {
            "type": "mcp_toolset",
            "mcp_server_name": "microsoft-learn",
            "default_config": {"permission_policy": {"type": "always_allow"}},
        },
    ],
    skills=[{"type": "anthropic", "skill_id": "docx"}],
)
print(f"agent        {agent.id}  version={agent.version}")

environment = client.beta.environments.create(
    name=f"learn-brief-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)
print(f"environment  {environment.id}")

session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Docs brief from MCP and a skill",
)
print(f"session      {session.id}")
print(f"trace        https://platform.claude.com/workspaces/default/sessions/{session.id}\n")

client.beta.sessions.events.send(
    session.id,
    events=[
        {
            "type": "user.message",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Search Microsoft Learn for what Azure Container Apps bills for. "
                        "Then use the docx skill to write "
                        "/mnt/session/outputs/container-apps-brief.docx with a heading, "
                        "three bullet findings, and the doc URLs you used."
                    ),
                }
            ],
        }
    ],
)

seen = 0
while True:
    current = client.beta.sessions.retrieve(session.id)
    log = list(client.beta.sessions.events.list(session.id, order="asc"))
    for event in log[seen:]:
        if event.type == "agent.mcp_tool_use":
            print(f"  mcp_tool_use  {event.name} {event.input}")
        elif event.type == "agent.tool_use":
            print(f"  tool_use      {event.name} {str(event.input)[:70]}")
        elif event.type == "agent.message":
            text = "".join(block.text for block in event.content)
            print(f"  message       {text[:200]}")
        elif event.type == "session.status_idle":
            print(f"  status_idle   stop_reason={event.stop_reason.type}")
    seen = len(log)
    idle = [event for event in log if event.type == "session.status_idle"]
    if current.status == "terminated" or any(
        event.stop_reason.type != "requires_action" for event in idle
    ):
        break
    time.sleep(3)

time.sleep(4)
output_dir = Path(__file__).parent / "outputs"
output_dir.mkdir(exist_ok=True)
for entry in client.beta.files.list(
    scope_id=session.id, betas=["managed-agents-2026-04-01"]
).data:
    target = (output_dir / entry.filename).resolve()
    client.beta.files.download(entry.id).write_to_file(target)
    print(f"\ndownloaded   {entry.filename}  {entry.size_bytes} bytes")
    print(f"saved to     {target}")

print(f"usage        {client.beta.sessions.retrieve(session.id).usage}")

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
print("Deleted the session and the environment. The agent stays reusable.")
