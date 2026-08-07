# Labs - Module 03: Skills

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Skill Authoring | [Package Invoice Generation Into a Skill Claude Fires on Its Own](lab-01-invoice-docx-skill.md) | Core | Intermediate | 1h 15m | Build a composite `invoice-docx` skill: triggering frontmatter, restricted `allowed-tools`, the layout contract in `references/`, the rendering in a docx-js script, and today's date injected at load time. |
| 02 | Skills as Services | [Serve the Same Document Generator to Clients That Are Not Claude](lab-02-invoice-document-api.md) | Optional | Intermediate | 45m | Refactor the renderer so one module serves both the CLI and an HTTP endpoint, return real `.docx` bytes over POST, verify the package is valid, then decide when the skill should call the service instead of rendering locally. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 15m. All labs: 2h.

Both labs run on Node 18 or newer and need one `npm install` each; nothing else is required, and no account or key is involved.

Each lab works in its own starter (`invoice-skill/` and `invoice-api/`) with the finished counterpart beside it (`invoice-skill-solution/` and `invoice-api-solution/`). The starters stay pristine (no dependencies, no generated documents); install, run and generate only inside your working copy or the solution folders. Lab 02's starter already ships the renderer that Lab 01 produces, so it stands alone if you run it first or on its own.

Authoring a skill around an MCP server moved to [Module 04](../04-mcp/lab-05-authoring-an-mcp-python-skill.md), because it needs MCP, which this module has not covered yet.
