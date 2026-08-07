# Make Claude Reason Deeper on Hard Decisions

`STATE.md` already carries the locked constraints and keeps one architectural question open: which BM25 ranking expression the search command should use.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python notes.py add "hello world"
python notes.py add "second note"
python notes.py list
```

On macOS or Linux, activate with `source .venv/bin/activate`.

Expected output of `python notes.py list`:

```text
2  2026-07-22 20:38:22  second note
1  2026-07-22 20:38:21  hello world
```

`python notes.py search hello` fails with `No such command 'search'` until the migration and the command exist.

The completed reference version (FTS5 migration with sync triggers, the ranked `search` command, a test file, and a fully checked STATE.md) lives in [../notes-cli-solution/](../notes-cli-solution/).
