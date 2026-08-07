# Memory Architectures Starter

Starter project for [`lab-03-memory-architectures.md`](../../lab-03-memory-architectures.md). Open Claude Code in this folder and work here. The completed reference is beside it in [`memory-lab-solution/`](../memory-lab-solution/readme.md).

## What ships here

| Path | Role |
|---|---|
| `notes/topic-*.md` | The eight-note Lumen corpus, the fixed input every architecture is measured against |
| `recall-questions.txt` | The three recall questions, the fixed 70-token overhead every architecture pays |
| `tokens.py` | The `tiktoken` token counter from Lab 01, so all four architectures are measured with one instrument |
| `.gitignore` | Keeps `.venv/`, `results/`, the graph store and the auto-memory store out of version control |

Measured with `cl100k_base`: the eight notes total 2,859 tokens for 1,816 words, and `recall-questions.txt` is 70 tokens. Those are the same numbers the solution reports, so your Step 1 measurement should match it exactly.

## Install

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install tiktoken
./.venv/Scripts/python.exe tokens.py notes/topic-architecture-overview.md
```

On Linux or macOS use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

## What you build

`notes/STATE.md`, `.mcp.json`, `.claude/settings.json`, the `auto-memory/` store Claude Code writes into it, and everything under `results/`: the in-context run, the statefile run, the knowledge-graph run, the auto-memory run, the four-way comparison, and the audit.

`.mcp.json` and `.claude/settings.json` both take an absolute path (`MEMORY_FILE_PATH` and `autoMemoryDirectory`), and neither resolves a relative one against this folder.
