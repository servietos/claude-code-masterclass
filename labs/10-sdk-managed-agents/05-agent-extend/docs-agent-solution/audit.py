import sys
from collections import Counter

from common import client

session_id = sys.argv[1]
tally = Counter()

for event in client.beta.sessions.events.list(session_id, order="asc"):
    if event.type == "agent.mcp_tool_use":
        route = "mcp"
        label = f"{event.name} {event.input}"
    elif event.type == "agent.tool_use":
        route = "skill" if "/workspace/skills/" in str(event.input) else "container"
        label = f"{event.name} {str(event.input)[:70]}"
    else:
        continue
    tally[route] += 1
    print(f"  [{route:<9}] {label}")

print(f"\ncontainer={tally['container']} mcp={tally['mcp']} skill={tally['skill']}")
