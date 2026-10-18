# Turn a Single Agent into a Graded Team with Memory

A demo starter for the three features of this topic. The script runs one agent that reads three regional feedback files and writes a digest; the demo guide turns it into a lead with a reader subagent, a graded outcome and a memory store.

## Prerequisites

- Python 3.11+
- `anthropic` 1.15.0 or later: memory stores need 0.122.0 or later, and the `multiagent_20261001` types ship in the 1.x line
- Your key in `.env` at the module root, which the script loads itself (see the [module readme](../../readme.md)), or `ANTHROPIC_API_KEY` already in the shell
- Network access to `api.anthropic.com`

## Run It

Both commands work unchanged in PowerShell.

```bash
cd demos/10-sdk-managed-agents/08-multiagent/feedback-digest
pip install -r requirements.txt
python digest.py
```

The finished version, with the reader subagent, the outcome rubric, the memory store and a session budget, lives in [`../feedback-digest-solution/`](../feedback-digest-solution/digest.py).
