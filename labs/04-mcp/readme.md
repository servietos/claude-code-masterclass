# Labs - Module 04: MCP

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Using MCP | [Modernize Angular with the Angular MCP](lab-01-modernizing-angular-mcp.md) | Optional | Intermediate | 1h 30m | Use the Angular MCP to evaluate and progressively modernize the food-shop-ng application with signal patterns, OnPush change detection, and zoneless architecture. |
| 02 | Building MCP | [Build the EventTrack Registration MCP Server](lab-02-eventtrack-mcp-server.md) | Core | Intermediate | 1h | Build a headless Python MCP server that manages events and attendee registrations, then drive the full registration workflow through Claude Code. |
| 03 | MCP Apps | [Drive an Interactive PDF Viewer with MCP Apps](lab-03-pdf-viewer-mcp-app.md) | Optional | Beginner | 45m | Build and register the PDF MCP server, then open, navigate, annotate and save documents inside Claude Desktop's embedded viewer. |
| 04 | MCP Apps | [Fly a 3D Globe with the Map MCP App](lab-04-map-mcp-app.md) | Optional | Intermediate | 45m | Build and run the Map MCP App, then use Claude Code to geocode landmarks and fly a 3D globe to their coordinates. |
| 05 | MCP + Skills | [Wrap a Python MCP App in a Custom Skill](lab-05-authoring-an-mcp-python-skill.md) | Optional | Advanced | 1h 15m | Use the QR Code MCP server in `src/qr-mcp-app-py` as a working reference, then use the `skill-creator` skill to extract its patterns into a reusable `mcp-python` skill for any future Python MCP project. |
| 06 | Artifact connectors | [Publish a Page That Reads Live Data Through a Connector](lab-06-connector-backed-artifact.md) | Optional | Intermediate | 1h 20m | Publish an issue board that fetches fresh GitHub records through your claude.ai connector on every open, then check from a second account what it shows and who may open it. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h. All labs: 6h 35m.

Lab 03 additionally requires Claude Desktop, since Claude Code cannot render an MCP App.

Lab 06 needs the GitHub connector on your claude.ai account, Claude Code v2.1.209 or later, and a second claude.ai account to open the published page from.

Lab 05 was Module 03's lab until it moved here: it authors a skill, but everything it reads is MCP server anatomy, which Module 03 has not covered yet. Run it after Lab 02 and the reference server will already make sense. It works in `04-mcp-skills/mcp-python-skill/` and mines `src/qr-mcp-app-py/`.

Each lab has a starter project folder you build in, and a finished counterpart beside it named `<starter>-solution/`. The starter stays pristine (no dependencies, no build output, no database); install, run and generate only inside the solution folder, and use it as the completed reference when you want to compare.
