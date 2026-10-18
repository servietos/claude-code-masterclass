# notes-toolkit

Inventories `TODO`, `FIXME` and `NOTE` comments across a project and triages them into `Now`, `Next` and `Later`.

## Contents

| Component | Invoked as |
|---|---|
| Skill `notes-extract` | `/notes-toolkit:notes-extract` |
| Skill `notes-prioritise` | `/notes-toolkit:notes-prioritise` |
| Command `notes-flow` | `/notes-toolkit:notes-flow` |
| Hook `scope-gate` | `PreToolUse` on `Write` and `Edit` |
| MCP server `notes-mcp` | tool `count_todos` |

## Use locally

```bash
claude --plugin-dir /full/path/to/notes-toolkit
```
