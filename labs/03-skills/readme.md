# Labs - Module 03: Skills

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Skill Authoring | [Package Invoice Generation Into a Skill Claude Fires on Its Own](lab-01-invoice-docx-skill.md) | Core | Intermediate | 1h 15m | Build a composite `invoice-docx` skill: triggering frontmatter, pre-approved `allowed-tools`, the layout contract in `references/`, the rendering in a docx-js script, and today's date injected at load time. |
| 02 | Skills as Services | [Serve the Same Document Generator to Clients That Are Not Claude](lab-02-invoice-document-api.md) | Optional | Intermediate | 45m | Refactor the renderer so one module serves both the CLI and an HTTP endpoint, return real `.docx` bytes over POST, verify the package is valid, then decide when the skill should call the service and when it should render locally. |
| 03 | Skill Catalog | [Install a Catalog Skill and Let It Shape Real Code](lab-03-install-a-catalog-skill.md) | Optional | Beginner | 45m | Find a DOCX skill with `/find-skills`, confirm what the install changes, install it into the lab's own `.claude/skills/`, read back its triggers and `allowed-tools`, and let it shape a program that writes a `.docx` delivery note. |
| 04 | Live Data & Subagents | [Fork a Skill into a Subagent](lab-04-fork-a-skill-into-a-subagent.md) | Optional | Intermediate | 50m | Inject live `grep` and line-count output with `` !`command` ``, fork the evidence-heavy reading into an Explore subagent with `context: fork`, and compare what it leaves in your session against an inline variant with `/context`. |
| 05 | Test & Package | [Test a Skill Until It Is Safe to Hand Over and Package It](lab-05-test-and-package-a-skill.md) | Optional | Intermediate | 1h 30m | Prove a release-notes skill fires on the right prompts and stays quiet on the wrong ones with a headless `claude -p` trigger matrix, grade its output against five properties, patch the description and the body where each failure lives, and package the skill as an installable folder and archive. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 15m. All labs: 5h 5m.

Labs 01 to 03 run on Node 18 or newer and need one `npm install` each; Labs 04 and 05 need no install. No account or key is involved.

Each lab works in its own starter (`invoice-skill/`, `invoice-api/`, `catalog-skill/`, `fork-skill/` and `release-bench/`); Labs 01 and 02 have the finished counterpart beside them (`invoice-skill-solution/` and `invoice-api-solution/`). The starters stay pristine (no dependencies, no generated documents); install, run and generate only inside your working copy or the solution folders. Lab 02's starter already ships the renderer that Lab 01 produces, so it stands alone if you run it first or on its own.

Authoring a skill around an MCP server moved to [Module 04](../04-mcp/lab-05-authoring-an-mcp-python-skill.md), because it needs MCP, which this module has not covered yet.
