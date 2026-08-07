# Calc Triage Solution

The completed reference for [`../../lab-01-managed-agent-codebase-triage.md`](../../lab-01-managed-agent-codebase-triage.md). You work in the starter at [`../calc-triage/`](../calc-triage/readme.md) and write `triage.py` and `gated_commit.py` there; this folder exists so you can compare when something does not line up.

## What Is Here

| File | Role |
|------|------|
| `calc.py` | Three functions, three planted bugs, one docstring contract each |
| `test_calc.py` | Three tests, one per bug |
| `triage.py` | Steps 1 to 4 and 7: agent, environment, session with two file mounts, SSE fix loop, output download, cleanup |
| `gated_commit.py` | Step 5: adds a `commit_changes` custom tool, parks the Session at `requires_action`, resumes with an allow or a deny verdict |
| `requirements.txt` | `anthropic>=0.118.0`, `python-dotenv>=1.0.0` and `pytest` |

## The Fixture Stays Broken

`calc.py` keeps its three bugs in both the starter and this solution, and that is deliberate. The Files API uploads a **copy**; the agent edits the container's copy, never the file on your disk. Running `pytest` locally is how you confirm the fixture is intact before a run, not how you check the agent's work.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q
```

Verified output on Python 3.12.10:

```text
3 failed in 0.04s
```

Each failure names one bug: `median` ignores the even-length case, `percent_change` raises `ZeroDivisionError` instead of the documented `ValueError`, and `running_total` is off by one. The agent's fixed `calc.py` lands in `outputs/` after a run, and `pytest` against that copy reports `3 passed`.

## Running the Scripts

Both scripts create real Managed Agents resources and bill session-hours plus model tokens. Neither needs anything in your shell: each one loads `ANTHROPIC_API_KEY` from [`demos/12-managed-agents/.env`](../../../../demos/12-managed-agents/), resolved from the script's own location.

```bash
.venv/Scripts/python triage.py
.venv/Scripts/python gated_commit.py
```

`gated_commit.py` blocks on `input()` at the gate, so run it in a real terminal. Reuse the agent across both scripts with `export MANAGED_AGENT_ID=agent_...` to avoid publishing a second one.

Both delete their Session, their Environment and their uploads on the way out; the Agent stays published because it costs nothing at rest. A run that dies before that block leaks a billed Environment, so list and delete by ID after any crash:

```python
for s in client.beta.sessions.list():
    client.beta.sessions.delete(s.id)
for e in client.beta.environments.list():
    client.beta.environments.delete(e.id)
```

## The Trap Worth Reading

`agents.update` replaces array fields wholesale. `gated_commit.py` re-declares `agent_toolset_20260401` alongside the custom tool for exactly that reason: sending `tools=[COMMIT_CHANGES]` would strip bash, read, write, edit, glob and grep, leaving an agent that can call `commit_changes` and nothing else.
