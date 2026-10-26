# Running Tests While bin/ Is Locked

## Verifying while another process holds bin/

A running dev instance (`dotnet run` in another terminal or another session) locks
`bin/Debug/net10.0/<app>.exe`, and every build fails with MSB3021/MSB3027 on the file copy. That is
an environment lock, not a compile error, and killing the other process is not yours to do.

Redirect the output instead, and keep the redirect **inside the project**:

```bash
dotnet test <tests>.csproj --nologo -p:BaseOutputPath=bin/verify/ -p:NuGetAudit=false
```

Write it exactly as `bin/verify/`. A relative `BaseOutputPath` resolves against **each project's own
folder**, the referenced API project included, so the value must be project-relative. A
repo-root-relative string such as `src/<tests>/bin-verify/` lands in `src/<tests>/src/<tests>/...`,
and a sibling folder beside `bin/` is not gitignored and gets swept into the next build's content,
nesting one output inside the next. `bin/verify/` sits under the ignored `bin/` in every project.
Proven on vouchers-ai, 2026-09-11: 664/664 with no nesting and no untracked files; the
`src/<tests>/bin-verify/` form and an absolute folder at the repo root had left 180 MB of recursive
output there.

A path outside the project (a temp folder) builds and runs, but silently breaks anything deriving a
repo path from `AppContext.BaseDirectory`: a `MemberData` source walking up five levels lands
somewhere else, finds no files, and xUnit reports `No data found for <test>` — which reads exactly
like a real failure. The tell is the **total**: 49 tests instead of 60. Compare test counts between
runs, not only pass/fail, and delete the redirect folder afterwards.

**Keeping the redirect inside the project is the workaround; `[CallerFilePath]` is the fix.** A test
that reads a repo file (a SQL delta, a fixture, a schema) should not know where its own binary ended
up. The compiler bakes the source file's absolute path in at build time, so this survives any output
redirect, a container copy, and single-file publish:

```csharp
private static string RepositoryRoot([CallerFilePath] string callerFilePath = "") =>
    Path.GetFullPath(Path.Combine(Path.GetDirectoryName(callerFilePath)!, "..", ".."));

private static string ScriptPath => Path.Combine(RepositoryRoot(), "db", "myproj", "deltas", "x.sql");
```

The `..` count is now relative to the source file, which moves only when someone moves the file, and
it needs `using System.Runtime.CompilerServices;`. Prove it by running the suite once with
`-p:BaseOutputPath` pointed at a temp folder outside the repo: the counts must match the normal run.
Five tests in one repo passed for weeks and failed the moment the output moved, because they were
never wrong about the repo, only about where they were standing.

Back to the index: [dotnet-testing](dotnet-testing.md)
