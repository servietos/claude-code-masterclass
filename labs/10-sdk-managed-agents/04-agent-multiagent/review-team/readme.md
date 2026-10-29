# Review Team Starter

The starter for [`../../lab-04-agent-review-team-memory.md`](../../lab-04-agent-review-team-memory.md). It ships a small Python module with three planted defects, mounted into a cloud session for a team of reviewer agents; you write the three driver scripts yourself as the lab walks you through them.

## What Is Here

| File | Role |
|------|------|
| `inventory.py` | Four functions over SQLite; three of them break their docstring contract or trust user input |
| `test_inventory.py` | Three tests, one per defect |
| `requirements.txt` | `anthropic>=1.15.0`, `python-dotenv>=1.0.0` and `pytest` |

## What You Write

| File | Lab steps |
|------|-----------|
| `review.py` | Steps 1 to 9: memory stores, two reviewer subagents, the lead, the session with mounts, stores and a budget, the outcome, the stream, the thread drill-down, the download and the memory audit |
| `recall.py` | Step 10: a new session that answers from the Review History store |
| `cleanup.py` | Step 11: deletes both stores |

The finished versions of all three are in [`../review-team-solution/`](../review-team-solution/readme.md).

## The Fixture Stays Broken

The Files API uploads a copy, and the reviewers only read it, so `inventory.py` keeps its three defects for every run.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q
```

On Linux or macOS the interpreter is `.venv/bin/python`.

Verified output on Python 3.12.10:

```text
FAILED test_inventory.py::test_find_by_sku_treats_the_sku_as_data - assert ('...
FAILED test_inventory.py::test_restock_rejects_a_negative_amount - Failed: DI...
FAILED test_inventory.py::test_low_stock_includes_items_at_their_reorder_level
3 failed in 0.08s
```

## The Key

Every script you write loads `ANTHROPIC_API_KEY` from [`labs/10-sdk-managed-agents/.env`](../..), resolved from the script's own location, so there is nothing to export and nothing to source.
