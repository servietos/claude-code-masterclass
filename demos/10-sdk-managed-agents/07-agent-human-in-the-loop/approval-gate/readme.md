# Pause a Managed Agent on a Custom Tool Call

A 20-minute demo of the custom-tool handoff. The Agent drafts an invoice email, calls a tool your application owns, and the Session parks at `requires_action` until you return a result.

## Prerequisites

- Python 3.11+
- Your key in `.env` at the module root, which the script loads itself (see the [module readme](../../readme.md)), or `ANTHROPIC_API_KEY` already in the shell
- Network access to `api.anthropic.com`

## Run It

```bash
cd demos/10-sdk-managed-agents/07-agent-human-in-the-loop/approval-gate
pip install -r requirements.txt
python demo.py
```

The finished version, which returns the tool result and handles a deny verdict, lives in [`../approval-gate-solution/`](../approval-gate-solution/01-approval-gate.py).
