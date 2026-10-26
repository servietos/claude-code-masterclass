# MSB3027: a build that fails only on the copy step

## A build that fails only on the copy step, on a checkout shared with other sessions

```text
error MSB3027: Could not copy "obj\Debug\net10.0\apphost.exe" to "bin\Debug\net10.0\app.exe".
Exceeded retry count of 10. Failed. The file is locked by: "app (68264)"
```

The compile succeeded. Read the error list before reacting: `MSB3021`, `MSB3026` and `MSB3027` are
the copy step, and a run that reports them and nothing else has already produced a valid assembly.
The lock is a running instance of the app holding its own exe.

**Read the error CODE before the message.** An `MSB3xxx` file-copy lock is a process problem and a
`CSxxxx` is a code problem, and only the second is a reason to open a source file. The failure this
prevents is not a slow diagnosis, it is a false one: the output says "Build FAILED", so a session
that reads the message and not the code edits code that was already correct, or reports the build as
broken and files it as a limitation it cannot fix. The fix is to stop the process, or to build a
project the running app does not lock, or to build to a scratch directory as above.

**Whose instance it is decides what you may do.** On a checkout several sessions share, the pid in
the message is often not yours. Check before killing it:

```bash
# what it is, and since when
powershell -c "Get-Process -Id <pid> | Select-Object Id,ProcessName,@{n='Started';e={\$_.StartTime}}"
netstat -ano | grep LISTENING | grep "\s<pid>\$"
```

A process you started this session is yours to stop. One started hours earlier belongs to someone
else's work: ask before `taskkill //PID <pid> //F`, and say in the report that you killed it.

**To prove the code compiles without touching anyone's process**, build to a scratch output:

```bash
dotnet build <proj>.csproj -p:BaseOutputPath="$TEMP/scratch/"
```

Redirect only the OUTPUT path. Redirecting `BaseIntermediateOutputPath` as well produces
`CS0579: Duplicate 'System.Reflection.AssemblyVersionAttribute'`, because the generated
`AssemblyInfo.cs` is then emitted twice, and that is a false failure of your own making.

`--artifacts-path` is the whole-project version and the safe one for a test run: `dotnet build` and
`dotnet test <tests>.csproj --artifacts-path <short scratch dir>` move `bin` and `obj` of every
project in the graph, so nothing collides with a running `dotnet watch`. On 2026-10-24 it built and
tested ten projects beside their live servers with no `CS0579`. Keep the path short: under a long
scratchpad folder 29 tests failed with `DllNotFoundException` for `Microsoft.Data.SqlClient.SNI.dll`
("filename or extension is too long", 259 characters), and a two-level folder fixed it.

Confirm the scratch assembly is the new code rather than a cached copy, by looking for a symbol
that only exists after the change:

```bash
grep -a -o -E "GetDetailBy[A-Za-z]+" "$TEMP/scratch/Debug/net10.0/<app>.dll" | sort -u
```

`strings` is not present in Git Bash on Windows; `grep -a` over the dll does the same job here.

**When all you need is the compiler's verdict, skip the scratch output entirely** and stop before the
copy step that takes the lock:

```bash
dotnet build -t:Compile --no-incremental
```

`-t:Compile` runs `CoreCompile` without the `Build` target's copy-to-`bin`, so a held exe cannot fail
it. Add `--no-incremental` or an unchanged-looking project answers "All projects are up-to-date" and
never recompiles your edit. Judge the run ONLY on lines matching `error CS` or `warning CS`:

```bash
dotnet build -t:Compile --no-incremental 2>&1 | grep -E "(error|warning) CS"
```

An empty result is the pass. `MSB3021`, `MSB3026` and `MSB3027` may still appear in the same output
when MSBuild reaches the copy anyway; they are the lock, not the code. On a project with
`TreatWarningsAsErrors`, this is the check that tells you whether the tree is clean.

Say what this did and did not prove: the code COMPILES; it was not linked, not started, and no
endpoint was exercised. Report that gap rather than letting "build passed" stand in for it.

Back to the index: [dotnet-cli](dotnet-cli.md)
