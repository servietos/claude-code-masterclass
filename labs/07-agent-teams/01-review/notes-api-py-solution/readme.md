# notes-api-py

A dependency-free notes service on `http.server`. It lists notes, reads one by name, searches across all of them, and accepts a write behind a token header.

```bash
python notes_api.py
```

```bash
curl http://127.0.0.1:8080/notes
curl "http://127.0.0.1:8080/search?q=retention"
```

| File | Role |
|---|---|
| `notes_api.py` | HTTP handler and routing |
| `store.py` | File-backed list, read, write, and search |
| `config.py` | Port, notes directory, and the write token |
| `notes/` | Three sample notes the service serves |

Nobody has reviewed it. It has never been load tested, it has no tests at all, and it has not been through a security pass.
