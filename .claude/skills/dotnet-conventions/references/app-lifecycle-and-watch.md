## When to use

Starting/reusing a running app instance, or diagnosing a `TypeLoadException` after editing code
under a running `dotnet watch`.

## Application Lifecycle

- Before starting the application, check if an instance is already running; if it is running under
  `dotnet watch run`, reuse that instance instead of starting a new one.
- Never start the application as a background process.
- Always dispose of resources properly when the application closes.
- **Hot-reload limits under `dotnet watch`**: structural edits (new methods, added queries/branches
  in controllers or services, signature changes) are rude edits. Hot reload fails with
  `TypeLoadException` and the process then serves that exception for every request while stuck on
  its interactive restart prompt; file touches do not recover it. After any structural edit under a
  running watch, verify with a real HTTP request; if the response is a `TypeLoadException`, ask the
  user to restart the watch (`Ctrl+R` in its terminal). Never kill a watch process you did not start.
- **A red build is the silent case, and it looks like a healthy process.** When the rebuild fails to
  compile, the watch keeps answering from the last good build: no `TypeLoadException`, no error in
  any response, just old behaviour. A `200` proves the process is alive, never that it is running
  your code. After editing under a running watch, build to a scratch directory
  (`dotnet build <proj> -o <scratch>`, because the watch holds `bin/Debug/<tfm>`) and look for a
  symptom only the new code could produce, rather than trusting the endpoint to fail loudly.
- **The route table is snapshotted at startup too, and a stale one 404s in a way that reads as a
  coding error.** Hot reload covers method bodies; a new controller action changes routing, which
  needs a restart. Until then the app answers from the OLD route table, so `GET /api/things/export`
  falls through to `[HttpGet("{name}")]` and returns a well-formed `problem+json` 404 for a thing
  named "export". Every other endpoint stays green and the build is clean, so nothing points at the
  process. Before editing code to chase it, check what is actually listening and how old it is:
  `Get-NetTCPConnection -LocalPort <p>` then the owning process's `StartTime`, compared against the
  source file's mtime. Touching a file does not force the restart. To prove the code without taking
  the user's process, build a copy (`scripts/build-copy.sh --root <repo> --out <scratch> --path
  <api> --test <tests>`: repo layout kept, bin/obj excluded). Redirecting `obj` with
  `-p:BaseIntermediateOutputPath` does not work: the project's own `obj/*.AssemblyInfo.cs` is still
  globbed and the build dies on `CS0579` duplicate attributes. Note also
  that a literal segment always outranks a parameter segment, so adding `/export` permanently
  shadows an entity literally named `export` on `/{name}`.
- **`/openapi/v1.json` is the route table the process actually has, and it settles this in one call.**
  When a route moves rather than appearing (the repo-wide "route parameters last" refactor turned
  `/api/Apps/{appId}/settings` into `/api/Apps/settings/{appId}`), the stale process 404s every write
  while every GET stays green, which reads exactly like a broken payload or a missing record. Two
  cheap discriminators, in order: call the same route with a deliberately invalid id, because a
  `NotFound()` from the action and a route miss are both 404 but only a route miss survives a
  guaranteed-absent id; then `curl -s http://localhost:<port>/openapi/v1.json` and diff the paths
  against the source's `[Http*]` attributes. On 2026-09-06 that comparison showed the running
  `secrets-mcp` still serving the pre-refactor shape and missing `/api/Apps/box/{appId}` outright.
  Never edit source to chase a 404 you have not proven the running build serves.
- **On an `[Authorize]`d controller the cheapest probe needs no token and no id: authorization runs
  after routing, so a route the process has returns `401` and a route it does not have returns
  `404`.** Send the call with no credentials at all, and send a deliberately bogus sibling path in
  the same breath as the control, so the pair reads as evidence rather than as one status code:

  ```bash
  curl -s -o /dev/null -w "new:%{http_code}\n"    -X PUT http://localhost:5093/api/apps/name/<id>    -H "Content-Type: application/json" -d '{"name":"probe"}'
  curl -s -o /dev/null -w "bogus:%{http_code}\n"  -X PUT http://localhost:5093/api/apps/zzz/<id>     -H "Content-Type: application/json" -d '{}'
  ```

  `new:404 bogus:404` is a stale route table; `new:401 bogus:404` is the new action live. On
  2026-09-07 that pair caught a `PUT api/apps/name/{appId:guid}` that a subagent had shipped, built
  and tested green while the running watch still 404'd it, and the same two commands after the
  restart were the receipt that it was serving. This beats the invalid-id trick on any authorized
  API, because a `NotFound()` from the action can never be reached without a token, and it beats
  the `/openapi/v1.json` diff when that document is itself behind the auth gate.
- **The MCP tool catalog is built once at startup and hot reload never rebuilds it.**
  `WithToolsFromAssembly()` snapshots the tool list and its JSON schemas at boot, so a new
  `[McpServerTool]`, a rename, or a parameter that just became optional stays invisible while
  ordinary endpoints reflect the new code. Check `tools/list` for the tool name before debugging its
  behaviour, and expect one restart per tool-surface change. See
  [`dotnet-mcp.md`](dotnet-mcp.md).
- **The EF Core model is also built once at startup.** Hot reload applies a new navigation property
  to the class, but the cached model does not know it, so the first query that includes it throws
  `The expression 'e.Absences' is invalid inside an 'Include' operation, since it does not represent
  a property access` and the endpoint returns 500. A new entity, DbSet or navigation needs a real
  restart. Read that exception right after a model change as "restart pending", not as a code bug.
  A new scalar property is worse because it fails silently: the watch printed "C# and Razor changes
  applied", no exception came, and the API kept returning the new field as null although the row
  held a value. After any entity property change, read one row back through the API; a null that
  the database contradicts means restart, not debug.
- **Stop the watch before an agent edits the API across several files.** The watch hot-reloads every
  save, so a delegate's half-finished change (a service that references a column the entity does not
  have yet) is served live: every call returns 500 and any browser check run meanwhile fails on
  something unrelated. If you own the watch, stop it before the brief, let the agent build and test,
  and restart it after the report. If the user owns it, tell the agent not to build and say the
  watch will serve broken code until the edit is finished.
- **Never ANNOUNCE a restart, probe for one.** Hot reload covers more than the rude-edit cases above
  suggest: per Microsoft Learn it applies method bodies, new methods on existing types and whole new
  types, and whether the app comes back after a rude edit depends on that watch's own setting. A
  `DELETE` action added to a live controller under `dotnet watch run` was serving `204` on the next
  request with no user action, after the session had already told the user "the API will need a
  restart" and been corrected. And a rude edit does not silently restart either: `dotnet watch`
  PROMPTS `Do you want to restart your app - Yes (y) / No (n) / Always (a) / Never (v)?` in the
  user's terminal unless `--non-interactive` or `DOTNET_WATCH_RESTART_ON_RUDE_EDIT` is set. So both
  confident sentences are wrong. Probe the endpoint, then report what the probe said and name which
  case you are in. Which edits fall in which case, per Microsoft Learn:
  [`dotnet-watch-restart-matrix.md`](dotnet-watch-restart-matrix.md).
- **The rule covers what you RELAY, not only what you assert.** A subagent that changed the code
  will close its report with "the running `dotnet watch` needs a restart", and passing that to the
  user feels like reporting rather than claiming. It is the same claim with someone else's name on
  it, and the one-command probe that settles it is still yours to run. This was breached on
  2026-09-05, three replies running, by a session that had written the bullet above the same day:
  the delegate's claim happened to be true, and there was still no evidence for it until the probe
  came back `404` on the new route and `200` on the old one. Quote the status codes, not the agent.
- **A restart you announce may be one your own design created.** ASP.NET Core loads
  `appsettings.json` with `reloadOnChange: true`, so a value edited on disk is live in
  `IConfiguration` within milliseconds and no restart is needed. Binding it once at startup into a
  POCO singleton (`builder.Configuration.Get<AppConfig>()`, then `AddSingleton(cfg)`) throws that
  away: the snapshot is frozen at boot and every later edit to the file needs a process restart to
  take effect. On 2026-09-07 that turned setting one `GitHub:ClientId` into "restart 5093 again",
  one restart after a genuine one, and the answer was "not every change needs a dotnet restart
  especially not this ... i am fed up with your restart orgy". A value that a human edits between
  runs (a client id, a feature flag, an endpoint) is read at call time from `IConfiguration` or
  through `IOptionsMonitor<T>`, never from a startup-bound singleton:

  ```csharp
  public sealed class GitHubOAuthService(IHttpClientFactory factory, IConfiguration configuration)
  {
      private string? ClientId => configuration["GitHub:ClientId"];
  }
  ```

  Before reporting that a config change needs a restart, check WHY it does. If the answer is a
  startup-bound binding rather than the framework, the defect is the binding: fix it, and the
  restart disappears along with it. Keep the startup POCO for values that are structural at boot
  (connection strings, auth scheme wiring, CORS origins); it is wrong only for what a person edits
  while the app runs.

- **The same startup snapshot exists outside .NET, and there it never self-heals.** A dev server
  reads its own build configuration once at boot: adding `.postcssrc.json` to a running Angular
  server leaves it serving the unprocessed stylesheet (5,407 bytes against 18,144) with no error
  anywhere. Config the server reads at startup is the one case where a restart request is correct
  rather than lazy.
- **Restarting the watch is the user's job, and "I will just start my own" is how you take their
  port.** A restart needed for a rude edit gets reported and waited on, never performed. If a kill
  is explicitly approved, kill the whole ancestry, not the listening process: the chain is
  `dotnet watch` (or a `nohup` wrapper) -> `dotnet-watch.dll run` -> `dotnet run` -> the app exe, and
  killing only the app makes the watcher relaunch it within seconds, which reads as "the port freed
  itself and something else grabbed it". Verify the port is actually free
  (`netstat -ano | grep :<port>`) before reporting done. A watcher you started and thought you killed
  will otherwise hold the port and fail the user's own start with
  `AddressInUseException: address already in use`, with the blame pointing at their terminal.
  On Windows, walk the ancestry rather than guessing at it, because only the top of the chain is the
  watcher and only the listener is visible from the port:

  ```powershell
  $pid = (Get-NetTCPConnection -LocalPort 5093 -State Listen).OwningProcess
  $p   = Get-CimInstance Win32_Process -Filter "ProcessId=$pid"
  $par = Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)"
  Get-CimInstance Win32_Process -Filter "ProcessId=$($par.ParentProcessId)"   # dotnet-watch.dll run
  ```

  Stop the grandparent first, then the parent, then the listener, and confirm with
  `Get-NetTCPConnection -LocalPort <p> -State Listen` returning nothing.

  **Never restart it with `Start-Process`.** On Windows that opens a real console window on the
  user's desktop, one per call, and they outlive the session: a run that restarted an API and a dev
  server a few times left a row of stray terminals on screen and drew "never ever spin up a terminal
  again". Nothing in a normal session had ever done this before, so the windows read as the agent
  breaking something rather than as a restart.

  The server belongs to the user. Hand the command back and stop:

  ```text
  dotnet watch run     # from <proj>
  ```

  When a restart genuinely has to happen inside the session, run it through the agent shell's own
  background execution (the Bash tool's `run_in_background`), which spawns no window, redirect stdout
  and stderr to a scratch file, and poll the port until it listens rather than sleeping a fixed
  interval. Kill what you started before the session ends, and say so.
