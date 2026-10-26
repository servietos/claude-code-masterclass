# Long-running runs: start with 202, execute in a worker, let the SPA resume

Use when a user-triggered operation (run an agent now, import a file, regenerate a report) can take
longer than a comfortable HTTP request. The request must return at once with a run id; the work runs in
a background worker; the SPA follows the run and can leave and come back.

Proven in vouchers-ai (`AgentsController`, `AgentRunQueue`, `AgentRunWorker`, `with-agents.feature.ts`)
after mapping bico planner-ui's import pipeline, which had the right server shape and a broken client
transport.

## Server contract

1. **Persist the run before enqueueing.** `POST .../runs` inserts a run row (`Status = Queued`,
   `TriggeredBy = manual`, `QueuedAt`) and only then writes the id to the queue, returning
   `202 Accepted` with `{ RunId }`. The id is durable before the worker has seen it.
2. **Refuse a second concurrent run with 409** when a `Queued`/`Running` row exists for the same target.
   An unguarded run-now lets a manual and a scheduled run overlap.
3. **One queue, one reader.** `Channel.CreateUnbounded<int>(new() { SingleReader = true })` as a
   singleton; the worker is a `BackgroundService` doing `await foreach` and one DI scope per item. Queue
   ids, never payloads: file bytes in an in-memory channel are lost on restart.
4. **Persist every phase.** The worker sets `Running`, `StartedAt`, `Stage`, then `Succeeded` with its
   output rows, so one `GET .../runs/{id}` rebuilds the whole state. A snapshot endpoint needs no replay
   protocol.
5. **Write failure in a fresh scope.** On exception, create a new scope and `DbContext` to write
   `Failed` and the truncated `Error`: the scope that threw may hold a poisoned context.
6. **Sweep orphans at startup.** Before reading the queue, mark `Queued`/`Running` rows `Failed` with a
   restart message. Otherwise a restart leaves runs spinning forever in the UI.
7. **Status values are a closed set** (`Queued | Running | Succeeded | Failed`) shared as constants on
   both sides, never free strings.

Schema for the run table follows the repo's schema-change rule (SQL delta script where migrations are
banned: see [`sql-delta-scripts`](sql-delta-scripts.md)).

## Client contract

- **Never native `EventSource` behind bearer auth.** It cannot send the token, fails with 401 in
  production and silently degrades to polling. Follow runs through the app's existing `HttpClient`
  SSE stream (identity-only change frames, then refetch the snapshot), per `multi-client-sync`.
- **Fallback polling only while the stream is disconnected**, every 2 s, and only while the run is
  non-terminal.
- **Stale-run guard:** drop a snapshot whose `RunId` is not the active run.
- **Resume from the URL:** put `?runId=` in the route when a run starts; on load, fetch the snapshot and
  watch again. Leaving and returning then works with no client state.
- **Stop on terminal status**, then reload the list and detail once.

## Verify

- `curl -i -X POST .../runs` returns `202` and a `RunId`; a second call while it runs returns `409`.
- Kill the API mid-run, start it again: the run reads `Failed` with the restart message.
- In chrome-devtools, start a run, navigate away and back via the `?runId=` URL: status continues to
  update; with the SSE stream blocked, the snapshot request repeats every 2 s and stops at a terminal
  status.
