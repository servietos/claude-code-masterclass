# Review Team Solution

The completed reference for [`../../lab-04-review-team-memory.md`](../../lab-04-review-team-memory.md).

| File | Role |
|------|------|
| `review.py` | Creates or reuses the two memory stores, the two reviewer subagents and the lead, runs one graded review session, prints the threads and the memory versions, and downloads `review.md` to `outputs/` |
| `recall.py` | Answers a question about earlier reviews from a new session that mounts the Review History store read-only |
| `cleanup.py` | Deletes both memory stores and `stores.json` |

Run them in order from this folder; `review.py` writes `stores.json`, which the other two read.

```bash
python review.py
python recall.py
python cleanup.py
```

`outputs/` holds `not-executed.txt` until a run with a valid `ANTHROPIC_API_KEY` replaces it with the review.
