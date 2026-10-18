# session-loop-py

A dependency-free chat session loop. It should keep prompting until the user types `/quit`, and `config.json` sets `maxTurns` to 20.

It does not. The loop ends after the first exchange, and the closing line reports a turn count that does not match what a reader expects either.

```bash
printf 'hello\nsecond message\n/quit\n' | python session_loop.py
```

```powershell
"hello`nsecond message`n/quit" | python session_loop.py
```

| File | Role |
|---|---|
| `session_loop.py` | Entry point and the read, handle, reply loop |
| `session.py` | Session state, turn history, and the `is_open` predicate the loop tests |
| `config.py` | Reads `config.json` and applies defaults |
| `commands.py` | Handles `/help`, `/turns`, and `/quit` |
| `transcript.py` | Appends every message to `transcript.log` |
