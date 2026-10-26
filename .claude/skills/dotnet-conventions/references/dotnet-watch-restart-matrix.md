## When to use

Before telling anyone that a running `dotnet watch run` needs a restart. Classify the edit with the
matrix below, then probe the live process. A restart request without a probe is not allowed.

Sources (Microsoft Learn): `dotnet watch` (learn.microsoft.com/dotnet/core/tools/dotnet-watch),
".NET Hot Reload support for ASP.NET Core" (learn.microsoft.com/aspnet/core/test/hot-reload),
"Supported code changes (C# and Visual Basic)"
(learn.microsoft.com/visualstudio/debugger/supported-code-changes-csharp), and Roslyn's
`EnC-Supported-Edits.md`, which those pages defer to for .NET 6+.

## The three buckets

### 1. Hot-reloaded: no restart, the next request runs the new code

- Any change inside a method body: statements, expressions, variables, `if`/`switch`, LINQ, lambdas,
  local functions, `async`/`await`, string interpolation.
- Adding methods, fields, properties, events, constructors or nested classes to an existing type.
- Adding whole new types (a new service class, DTO or helper).
- Generics, record structs, top-level statements, switch expressions.
- ASP.NET Core: an inline middleware delegate or a route handler delegate (minimal API lambda).

### 2. Rude edits: `dotnet watch` cannot apply them and asks what to do

Microsoft Learn's unsupported list, with the shapes it takes in a typical API:

| Unsupported edit | Looks like in practice |
|---|---|
| Renaming any code element | renaming a method, parameter, property, class |
| Deleting a namespace, type or member | removing a property, turning a `static` property into a `static readonly` field (delete + add) |
| Modifying a method signature | adding a parameter to a primary constructor (new DI dependency), adding a positional parameter to a `record`, changing a return type |
| Adding or modifying attributes | a new `[HttpGet("...")]` action, `[Authorize]`, `[FeatureGate]` moved between class and action |
| Modifying an interface | adding a member to `IStockService` |
| Adding an abstract, virtual or override member | a new `override` on an entity or base controller |
| Changing a property/event/indexer type | `int` to `decimal` |
| Adding a `using` statement block | wrapping existing code in `using (...) { }` |
| Modifying a static member already accessed by running code | editing a static initializer value after first use |
| Editing an active statement | the loop body of a `BackgroundService.ExecuteAsync` that is currently running |
| Iterators, `dynamic` | `yield return` methods |
| Source-generator output changing shape | adding a `[GeneratedRegex]` member (the class turns `partial`): seen live as `BadImageFormatException` from the type's constructor on every request, persisting across waits. A plain `static readonly Regex` is an ordinary hot-reloadable edit and fixed it without a restart |

What happens next depends on how the watch was started, not on the edit:

- Interactive (the default): it prints `Do you want to restart your app - Yes (y) / No (n) / Always
  (a) / Never (v)?` in the user's terminal and keeps serving the OLD code until someone answers.
- `Always` was answered earlier, `--non-interactive` was passed, or
  `DOTNET_WATCH_RESTART_ON_RUDE_EDIT=1` is set: it restarts on its own within seconds.
- `Never` was answered: it keeps the old code and stays silent.

So the same rude edit can need nothing (it already restarted), a keypress (`y` or `Ctrl+R`), or be
silently ignored. Only a probe tells which.

**A probe that cannot tell old from new proves nothing.** An EF query rewrite (date-range predicate,
dropped column, in-memory sort) returns the same status and often the same bytes, so curl reads
"live" either way. Seen live: after a fresh start, three rounds of query edits never reached the
process; every endpoint answered 200 with unchanged sizes, and a load test that "passed" had measured
the old code. Prove such an edit from the SQL the server actually received, matched to your call:

```sql
SELECT CONVERT(varchar(12), qs.last_execution_time, 114), SUBSTRING(st.text, 1, 120)
FROM sys.dm_exec_query_stats qs CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
WHERE qs.last_execution_time > DATEADD(second, -10, GETDATE()) AND st.text NOT LIKE '%dm_exec%';
```

Repeated deltas to one method can also corrupt it outright: an action converted to `async`, then
edited twice more, returned `500 BadImageFormatException` from the JSON serializer on every call while
its siblings stayed healthy. Both states need a real restart of the watch process, and a killed child
is not one: `dotnet watch` then waits for a content change, and a `touch` does not count.
Seen working on SDK 10.0.112, twice in one session, for a new `[HttpGet("page")]` action that hot
reload never applied: stop the app child (the `bin\Debug\...\<App>.exe` whose parent is
`dotnet run ... DOTNET_WATCH=1`), then set a `.cs` file's `LastWriteTime` to now; the watcher rebuilt
and served the new route within 25 seconds. Find the child with
`Get-NetTCPConnection -LocalPort <port> -State Listen`. This is still a restart: only with the
owner's go-ahead.

### 3. Applied but inert: no rude edit, no prompt, still old behaviour

ASP.NET Core runs some startup logic only once, so a hot-reloaded edit to it changes nothing until
the process restarts (Learn: "Some startup logic is only run once"):

- Middleware registration and ordering in `Program.cs` (except inline middleware delegates).
- Service registrations: `AddScoped`, `AddHttpClient(...)` options, `AddHostedService`.
- Route creation and configuration (except the handler delegate body).
- The EF Core model: `OnModelCreating` runs once per process, so a new mapped entity property, an
  `Ignore`/`Property` change or a new `DbSet` compiles and hot-reloads into the class, yet queries
  keep using the cached model and the new column reads as `null`. Seen live: DB row `Market =
  Tradegate`, API `"Market": null` for four minutes, correct immediately after `Ctrl+R`.
- Anything already constructed or cached: singletons, `static` state initialized before the edit,
  options bound once into a POCO at startup, reflection-built catalogs (MCP tool list, JSON
  serializer metadata caches unless a `MetadataUpdateHandler` clears them).

This bucket is the only one where a restart is genuinely required no matter how the watch is
configured.

## The procedure

1. Classify the edit with the buckets above. Bucket 1 needs no restart: probe and move on.
2. For buckets 2 and 3, probe the live process for a symptom only the new code can produce: the
   changed response field, the new route answering (`401` instead of `404` on an authorized API),
   the DB row the new code writes, `/openapi/v1.json` for the route table.
3. If the probe shows old behaviour, wait briefly and probe again: an auto-restarting watch needs a
   few seconds for the rebuild. Compare the listening process's start time with the edited file's
   mtime to see whether it restarted at all.
4. Only when the second probe still shows old behaviour, ask. Quote the probe, name the bucket, and
   say what fixes it: `y` at the watch prompt or `Ctrl+R` for bucket 2, a restart for bucket 3.

A delegate's "the API needs a restart" is an unprobed claim; the probe is still yours to run. See
[`app-lifecycle-and-watch.md`](app-lifecycle-and-watch.md) for the probes in detail, the red-build
case that looks like a healthy process, and why the restart itself is the user's job.

## Worked example

One edit set changed a scraped-price `record` from `(Name, Price, ...)` to `(Isin, Price, ...)`,
added two primary-constructor dependencies to a service, and turned three `static Guid { get; set; }`
properties into `static readonly Guid` fields: all bucket 2, under a watch that restarts on rude
edits. A probe fired right after the subagent reported its edits still showed the old matching
logic, and that single probe was relayed as "the API needs a restart". It did not: an auto-restarting
watch rebuilds and restarts within a few seconds, and while a delegate is still editing, every save
triggers another one. The later probe showed the new behaviour with no user action. One early probe
proves nothing; wait a few seconds after the LAST edit, probe again, and only then conclude.
