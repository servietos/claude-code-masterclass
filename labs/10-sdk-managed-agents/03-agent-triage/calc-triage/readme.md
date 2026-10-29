# Calc Triage Starter

The starter for [`../../lab-03-agent-codebase-triage.md`](../../lab-03-agent-codebase-triage.md). It ships the broken Python fixture the lab mounts into a cloud Session; you write the two driver scripts yourself as the lab walks you through them.

## What Is Here

| File | Role |
|------|------|
| `calc.py` | Three functions, three planted bugs, one docstring contract each |
| `test_calc.py` | Three tests, one per bug |
| `requirements.txt` | `anthropic>=0.118.0`, `python-dotenv>=1.0.0` and `pytest` |

## What You Write

| File | Lab steps |
|------|-----------|
| `triage.py` | Steps 1 to 4 and 7: agent, environment, session with two file mounts, SSE fix loop, output download, cleanup |
| `gated_commit.py` | Step 5: adds a `commit_changes` custom tool, parks the Session at `requires_action`, resumes with an allow or a deny verdict |

The finished versions of both are in [`../calc-triage-solution/`](../calc-triage-solution/readme.md).

## The Fixture Stays Broken

`calc.py` keeps its three bugs, and that is deliberate. The Files API uploads a **copy**; the agent edits the container's copy, never the file on your disk. Running `pytest` locally is how you confirm the fixture is intact before a run, not how you check the agent's work.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q
```

Verified output on Python 3.12.10:

```text
3 failed in 0.04s
```

On Linux or macOS use `.venv/bin/python` instead of `.venv/Scripts/python`.

Each failure names one bug: `median` ignores the even-length case, `percent_change` raises `ZeroDivisionError` instead of the documented `ValueError`, and `running_total` is off by one. The agent's fixed `calc.py` lands in `outputs/` after a run, and `pytest` against that copy reports `3 passed`.

## The Key

Both scripts you write load `ANTHROPIC_API_KEY` from [`labs/10-sdk-managed-agents/.env`](../..), resolved from the script's own location, so there is nothing to export and nothing to source.
