import json
import sys
from pathlib import Path
from uuid import uuid4

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
sys.stdout.reconfigure(encoding="utf-8")

client = Anthropic()
suffix = uuid4().hex[:8]
stores = json.loads((Path(__file__).parent / "stores.json").read_text())

historian = client.beta.agents.create(
    name=f"review-historian-{suffix}",
    model="claude-opus-5-5",
    system="You answer questions about earlier code reviews from the Review History store. Cite the dates of the entries you use.",
    tools=[{"type": "agent_toolset_20260401"}],
)
print(f"historian    {historian.id}")

environment = client.beta.environments.create(
    name=f"recall-env-{suffix}",
    config={"type": "cloud", "networking": {"type": "limited"}},
)

session = client.beta.sessions.create(
    agent=historian.id,
    environment_id=environment.id,
    title="Review recall",
    resources=[{"type": "memory_store", "memory_store_id": stores["history"], "access": "read_only"}],
)
print(f"session      {session.id}\n")

question = "What did earlier reviews of inventory.py find, and which finding had the highest severity?"

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": question}]}],
    )
    for event in stream:
        if event.type == "agent.message":
            print(" ".join(block.text for block in event.content if block.type == "text"))
        elif event.type == "agent.tool_use":
            print(f"[tool] {event.name}")
        elif event.type == "session.status_terminated":
            break
        elif event.type == "session.status_idle":
            print(f"[idle] stop_reason={event.stop_reason.type}")
            if event.stop_reason.type != "requires_action":
                break

client.beta.sessions.delete(session.id)
client.beta.environments.delete(environment.id)
print("\nDeleted the session and the environment.")
