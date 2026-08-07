# Research with an MCP Server and Write with a Skill

A 15-minute script that sends one task to a Managed Agent, prints every tool call in order, and shows what changes when a documentation MCP server and the `docx` skill are attached to the Agent.

## Prerequisites

- Python 3.11+
- Your key in `.env` at the module root, which the script loads itself (see the [module readme](../../readme.md)), or `ANTHROPIC_API_KEY` already in the shell
- Network access to `api.anthropic.com`; the Microsoft Learn MCP endpoint is public and needs no credentials

## Run It

```bash
cd demos/12-managed-agents/04-tools-mcp/learn-brief
pip install -r requirements.txt
python brief.py
```

The finished version, which attaches both extensions and downloads the artifact the agent wrote, lives in [`../learn-brief-solution/`](../learn-brief-solution/brief.py).
