# dotnet CLI: running tests

## Test

| Command | Description |
|---|---|
| `dotnet test` | Run all tests |
| `dotnet test --filter "ClassName=ItemsControllerTests"` | Run tests matching a class name |
| `dotnet test -v n` | Run tests with normal verbosity output |
| `dotnet test --logger "console;verbosity=detailed"` | Show each failure's Error Message and Stack Trace — `-v q`/`-v n` print only the `[FAIL]` names |
| `dotnet test -c Release` | Run the suite while the app is up under `dotnet watch` |

A running app locks `bin/Debug/<tfm>`, so a plain `dotnet test` against a project that references it fails
with `MSB3021`/`MSB3027` while the watch is up. The lock is on that one output directory, not on the
project: `-c Release` builds into `bin/Release/<tfm>` and runs green without touching the watch. Same
trick for a compile check, with `dotnet build <proj> -o <scratch>`. Never stop or kill a watch you did
not start just to get a green run. Neither flag makes the *running* process current, though: a rude
edit is not hot-applied, so a green Release suite says nothing about the code the live app is serving.

Back to the index: [dotnet-cli](dotnet-cli.md)
