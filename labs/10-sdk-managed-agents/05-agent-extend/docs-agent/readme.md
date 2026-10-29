# Docs Agent Starter

The starter for [`../../lab-05-agent-mcp-and-skills.md`](../../lab-05-agent-mcp-and-skills.md). It ships the shared helpers every script uses; you write the Agent definitions and the four scripts yourself as the lab walks you through them.

## What Is Here

| File | Role |
|------|------|
| `common.py` | Loads the key, builds the `Anthropic` client, and provides `send_task`, `record_run` and `watch`, a poll loop that hands every new event to a function you pass in |
| `requirements.txt` | `anthropic>=1.15.0` and `python-dotenv>=1.0.0` |

## What You Write

| File | Lab steps |
|------|-----------|
| `baseline.py` | Steps 1 and 2: the environment, an Agent with the built-in toolset only, and one turn |
| `extend.py` | Steps 3 and 4: the same Agent with an MCP server, its grant and a skill, plus the download |
| `audit.py` | Step 5: reads one session's event log and tallies which extension served each call |
| `gated.py` | Step 6: the grant without a permission policy |
| `cleanup.py` | Step 7: deletes every session and environment the lab created |

## Run It

```bash
pip install -r requirements.txt
python -c "import common; print('ready', common.suffix)"
```

## The Key

Every script loads `ANTHROPIC_API_KEY` from [`demos/10-sdk-managed-agents/.env`](../../../../demos/10-sdk-managed-agents), resolved from the script's own location, so there is nothing to export and nothing to source.
