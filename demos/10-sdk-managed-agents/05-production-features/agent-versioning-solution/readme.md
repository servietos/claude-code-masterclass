# Publish an Agent Version and Pin a Session to It

A 15-minute script that publishes an Agent, pins a Session to an explicit version, and prints the permission verdict the platform applied to each tool call.

## Prerequisites

- Python 3.11+
- Your key in `.env` at the module root, which the script loads itself (see the [module readme](../../readme.md)), or `ANTHROPIC_API_KEY` already in the shell
- Network access to `api.anthropic.com`

## Run It

```bash
cd demos/10-sdk-managed-agents/05-production-features/agent-versioning
pip install -r requirements.txt
python versioning.py
```

The finished version lives in [`../agent-versioning-solution/`](../agent-versioning-solution/versioning.py).
