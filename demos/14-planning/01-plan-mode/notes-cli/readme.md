# Turn a Vague Brief into a Working Feature

A minimal Python CLI with `add` and `list` commands backed by SQLite. The finished result of the walkthrough lives in [../notes-cli-solution/](../notes-cli-solution/).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python notes.py list
```

On macOS or Linux, activate with `source .venv/bin/activate`.

Seed two starter notes to confirm it works:

```bash
python notes.py add "hello from notes-cli"
python notes.py add "second note"
python notes.py list
```
