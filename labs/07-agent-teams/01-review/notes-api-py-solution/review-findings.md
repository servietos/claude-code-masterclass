# Review findings

First review of `notes-api-py`. Three reviewers worked in parallel over one checkout: `security` (config and request handling), `perf` (store and the search endpoint), `tests` (coverage across the folder). Findings below are ranked by severity, then by lens.

------

## Ranked findings

| # | Severity | Lens | File | Line | Description |
|---|---|---|---|---|---|
| 1 | Critical | security | `notes_api.py` | 27 | The by-name read slices the URL path straight into a filename, so `..`, `..\` and absolute paths all escape `NOTES_DIR` and read any file on disk without a token. |
| 2 | Critical | security | `config.py` | 1 | A live-looking API token is hardcoded in committed source and is retrievable anonymously through finding 1, so it gates nothing. |
| 3 | Critical | security | `notes_api.py` | 47 | The write path joins an attacker-supplied `name` with no containment check, so a POST with an absolute path creates a file anywhere on disk and returns 201. |
| 4 | Critical | tests | `readme.md` | 21 | No test file, `conftest.py`, `pytest.ini`, `pyproject.toml` or CI config exists anywhere in the folder, so every finding here ships with no regression guard and any fix lands unproven. |
| 5 | High | security | `notes_api.py` | 45 | `Content-Length` is trusted verbatim and `config.MAX_BODY` is referenced nowhere, so a declared length with no bytes sent stalls the single-threaded `HTTPServer` and blocks every other request. |
| 6 | High | perf | `store.py` | 26 | `/search` re-reads every note from disk on every request with no index or cache, so one query costs N file opens and O(N x L x W) word comparisons. |
| 7 | High | perf | `notes_api.py` | 52 | `HTTPServer` is not threading, so the full-corpus scan runs on the single serving thread and concurrent searches queue one at a time (4 clients measured at 4x the single-request wall time). |
| 8 | High | perf | `store.py` | 30 | Hits are appended per matching occurrence with no cap and no dedupe, so a common term returns a body many times larger than the corpus on disk (3.6 MB response and a 17.0 MB peak from a 1.1 MB corpus). |
| 9 | High | tests | `config.py` | 3 | `NOTES_DIR` is the relative string `"notes"`, so importing `store` from any other working directory makes `list_notes` raise `FileNotFoundError` and a runner started at the repo root fails before it can assert anything. |
| 10 | High | tests | `store.py` | 6 | `list_notes`, `read_note` and `write_note` take no directory argument and resolve `config.NOTES_DIR` at call time, so there is no seam to inject a temp directory and every test must mutate a process-global that nothing restores. |
| 11 | High | tests | `notes_api.py` | 52 | The server is constructed inside `main()` against the fixed `config.PORT` with no factory returning an unstarted server, so an end-to-end test cannot bind an ephemeral port without reimplementing `main`. |
| 12 | Medium | security | `store.py` | 18 | `open(path, "w")` truncates with no existence check, so a POST to an existing note name destroys it silently. |
| 13 | Medium | security | `notes_api.py` | 18 | No token check on any read path, which is the documented contract but makes the traversal a pre-auth primitive rather than a post-auth one. |
| 14 | Medium | security | `notes_api.py` | 46 | The request body is unvalidated: non-JSON, a missing `name` key and a non-numeric `Content-Length` each raise out of the handler and close the socket with no response instead of a 400. |
| 15 | Medium | security | `notes_api.py` | 28 | A missing note raises `FileNotFoundError` out of `store.read_note`, so the 404 at line 36 is unreachable for `/notes/` paths and the endpoint becomes a file-existence oracle. |
| 16 | Medium | perf | `notes_api.py` | 32 | A missing or empty `q` defaults to `""` and still runs the entire corpus scan, so the cheapest request to issue is a full-cost one that can never match (50.0 ms at N=1000 for zero hits). |
| 17 | Medium | perf, tests | `store.py` | 7 | `list_notes` returns every directory entry unfiltered, so one subdirectory under `notes/` makes `read_note` raise mid-scan at `store.py:12` and `/search` drops the connection after the corpus work is already paid. |
| 18 | Medium | tests | `notes_api.py` | 41 | The handler reads `config.API_TOKEN` off the imported module rather than an injected value, so no test can exercise two token configurations in one process without leaking state into every test that follows. |
| 19 | Medium | tests | `notes_api.py` | 10 | `_send` writes straight to `self.wfile` and `Handler` cannot be instantiated without a live socket, so status and body are assertable only through a real server socket, never as a unit. |
| 20 | Medium | tests | `store.py` | 17 | `write_note` truncates against the default relative `NOTES_DIR`, so any write test run from the project folder rewrites the three checked-in sample notes the read and search tests use as fixtures. |
| 21 | Low | security | `notes_api.py` | 41 | The token is compared with `!=`, which short-circuits on the first differing byte and leaks a prefix by timing; `hmac.compare_digest` is the fix. |
| 22 | Low | perf | `store.py` | 29 | `term.lower()` is recomputed inside the innermost loop, doubling the `str.lower()` calls per search (440,000 instead of 220,001 at N=1000) for a measured 4.5% cost. |
| 23 | Low | tests | `readme.md` | 6 | The only documented entry point is `python notes_api.py`, and with no `pyproject.toml`, `requirements.txt` or CI workflow a first test file has no declared runner or invocation. |

### Proven call paths

Each security finding was confirmed against a live instance driven by raw sockets, not `curl`, because `curl` normalizes `..` out of the request line before it is sent.

```text
1   do_GET (notes_api.py:26) -> name = url.path[len("/notes/"):] (27)
      -> store.read_note(name) (28) -> os.path.join(NOTES_DIR, name) (store.py:11) -> open(path) (store.py:12)
2   do_POST (38) -> self.headers.get("X-Api-Token") (40) -> compared to config.API_TOKEN (41) -> literal at config.py:1,
      itself served by path 1 via GET /notes/../config.py
3   do_POST (38) -> json.loads(...) (46) -> store.write_note(payload["name"], payload["body"]) (47)
      -> os.path.join (store.py:17) -> open(path, "w") (store.py:18)
5   do_POST (38) -> int(self.headers.get("Content-Length", "0")) (45) -> self.rfile.read(length) (46)
14  do_POST -> json.loads(self.rfile.read(length)) (46) -> payload["name"] (47) -> escapes to socketserver.handle_error
15  do_GET (26) -> store.read_note("nope.txt") (28) -> open (store.py:12) -> FileNotFoundError
17  do_GET (31) -> store.search (store.py:23) -> list_notes (7) -> read_note (26) -> open on a directory (12)
```

### Measured cost of one search

`perf` instrumented `builtins.open` and `store.read_note` against the real `store.py`. One `/search` costs N file opens plus N x L x W word comparisons and twice that many `str.lower()` calls, per request, with nothing amortised across requests.

| Corpus | Opens | Chars read | Word comparisons | `lower()` calls | ms |
|---|---|---|---|---|---|
| repo `notes/` (3 files) | 3 | 331 | 52 | 104 | 0.17 |
| N=10, L=20, W=10 | 10 | 11,190 | 2,200 | 4,400 | 0.66 |
| N=100 | 100 | 111,900 | 22,000 | 44,000 | 5.40 |
| N=1000 | 1,000 | 1,119,000 | 220,000 | 440,000 | 58.9 |

The write path measured clean and carries no perf finding: `write_note` wrote 1 MB in 0.97 ms as one open and one write, and nothing in it scales with note count.

### What the first test file must cover

`tests` scoped a single stdlib `unittest` file, `test_notes_api.py`, which needs a `notes_dir` parameter on the store functions and a `make_server(notes_dir, port=0)` factory before any case can run without monkeypatching the config module globally (findings 9, 10, 11).

Store level: `test_list_notes_uses_injected_directory` (10), `test_store_works_from_any_cwd` (9), `test_read_note_rejects_parent_traversal` (1, returns `SECRET\n` today), `test_write_note_rejects_parent_traversal` (3, creates `../pwned.txt` today), `test_write_note_does_not_clobber_existing` (12), `test_read_note_missing_raises_typed_not_found` (15), `test_search_ignores_subdirectories` (17), `test_search_reads_each_note_once` (6), `test_search_empty_term_reads_nothing` (16).

HTTP level, server bound on port 0: `test_get_note_traversal_returns_404` (1, returns 200 and `SECRET\n` today), `test_get_missing_note_returns_404` (15, drops the connection today), `test_get_notes_is_public` (13, pins `readme.md:3` intent), `test_post_without_token_returns_401` and `test_post_with_wrong_token_returns_401` (2, 21), `test_token_comparison_is_constant_time` (21), `test_token_is_not_a_source_literal` (2), `test_post_over_max_body_returns_413` (5), `test_post_content_length_exceeding_body_does_not_hang` (5, no response at all today), `test_post_non_numeric_content_length_returns_400` (5, 14), `test_post_malformed_json_returns_400` and `test_post_missing_body_field_returns_400` (14).

## Contested

- **Is the unbounded body an allocation problem or a stall?** `perf` framed finding 5 as unbounded memory growth triggerable by an authenticated client. `security` rejected both qualifiers while agreeing on High: no allocation is needed, since a large declared length with zero bytes sent stalls the single-threaded server at no bandwidth cost, and "authenticated" is not a real precondition because the token is anonymously readable through finding 1. Recorded once, as finding 5, with security's framing.
- **Are the traversal and the hardcoded token one finding or two?** `tests` ranks the chain (anonymous GET reads the token, then POST writes any file) as a single critical that outranks either half. `security` agrees the chain outranks both but keeps two rows, because the fixes are independent (move the secret out of source, confine the path) and fixing either alone leaves a real defect standing. Kept as findings 1, 2 and 3, with the chain noted here.
- **Are anonymous reads a defect?** `tests` needed a ruling to know whether its test should pass or fail today. `security` ruled intended design per `readme.md:3`, so a `test_get_requires_no_token` case is an intent assertion that passes now, while the by-name route is the failing half. Logged as finding 13 at Medium because it amplifies the traversal, not because public reads are wrong.
- **Is threading the fix for the serialization?** `security` and `tests` both read finding 7 as an argument for `ThreadingHTTPServer`. `perf` disproved it by measurement: swapping in the threading server made the same load worse (77.3 ms single and 310.0 ms for four clients, against 65.8 ms and 212.4 ms), because the scan is CPU-bound under the GIL. Finding 7 stands at High as a serialization defect, but the fix it argues for is not scanning the corpus per request.
- **Where does the unfiltered listing live?** `perf` anchored the subdirectory defect at `store.py:7`, where `os.listdir` returns entries it never filters; `tests` anchored it at `store.py:26`, where `search` feeds each entry to `read_note`. Both reproduced the same raise from `store.py:12` (`PermissionError` on Windows, `IsADirectoryError` on POSIX). Merged into one row, finding 17, at the listing, because that is where the filter belongs.

## Fix

`patcher` closed finding 1 in `do_GET` (`notes_api.py:21`), where `NOTE_NAME.fullmatch(name)` at line 31 now rejects any name outside `[A-Za-z0-9_-]{1,64}\.txt` with a 400 before `store.read_note` is reached. It changed no file: the guard was already present when `patcher` was spawned, its approved plan was verify-only, and its diff is empty. The same regex guards `payload["name"]` in `do_POST` at line 53, which closes the handler half of finding 3; the sink in `store.read_note` and `store.write_note` is still unconfined, so every other row above stands as written against the code as reviewed.

Verified against a live instance driven by raw `socket.create_connection` rather than `curl`, because `curl` normalizes `..` out of the request line before it is sent. Against the pristine starter, `GET /notes/../config.py` returned 200 with `API_TOKEN = "nt_live_8f21c0d4e7b94a15"` in the body. Against this folder, the same request returned 400 `{"error": "bad note name"}`, as did the encoded forms `%2e%2e%2fconfig.py` and `..%5cconfig.py`, while `GET /notes/retention.txt` still returned 200 with the note body and `GET /notes` still listed the three notes.

One methodology note for anyone repeating this: under Git Bash, MSYS path conversion rewrote the traversal on the wire to `GET C:/Program Files/Git/notes/../config.py`, which the stdlib handler rejects with its own 400. `MSYS_NO_PATHCONV=1` is required, or a green-looking 400 means the test never ran.
