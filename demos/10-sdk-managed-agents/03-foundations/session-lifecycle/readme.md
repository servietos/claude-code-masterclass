# Watch a Session Move Through Its States

A 10-minute script that creates all three Managed Agents resources, drives one Session from `running` to `idle`, and prints the event log. It uses polling rather than streaming, which keeps the state machine visible.

## Prerequisites

- Python 3.11+
- Your key in `.env` at the module root, which the script loads itself (see the [module readme](../../readme.md)), or `ANTHROPIC_API_KEY` already in the shell
- Network access to `api.anthropic.com`

## Run It

```bash
cd demos/10-sdk-managed-agents/03-foundations/session-lifecycle
pip install -r requirements.txt
python lifecycle.py
```

The finished version, which decodes event payloads and reports token usage, lives in [`../session-lifecycle-solution/`](../session-lifecycle-solution/lifecycle.py).
