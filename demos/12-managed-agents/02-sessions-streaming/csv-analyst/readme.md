# Build Your First Managed Agent End to End

A 25-minute live demo that touches every Managed Agents primitive in one flow: Agent, Environment, Session, file mount, SSE stream, and cleanup.

## Prerequisites

- Python 3.11+
- Your key in `.env` at the module root, which the script loads itself (see the [module readme](../../readme.md)), or `ANTHROPIC_API_KEY` already in the shell
- Network access to `api.anthropic.com`

## Run It

```bash
cd demos/12-managed-agents/02-sessions-streaming/csv-analyst
pip install -r requirements.txt
python demo.py
```

The finished version, which downloads the agent's output file, lives in [`../csv-analyst-solution/`](../csv-analyst-solution/demo.py).
