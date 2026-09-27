# Cause 1: the dev server is serving a stale bundle

## Cause 1: the dev server is serving a stale bundle

A long-running `ng serve` can keep serving an hours-old bundle indefinitely. It survives Ctrl+Shift+R,
`location.reload()`, and touching the file to bump its mtime, because the staleness is server-side: the
watcher missed the change or a rebuild failed and the server kept the last good output. A concurrent
process writing into `src/` (another agent, another editor, a `run build` in the same tree) makes a
half-written file transiently unresolvable, which is enough to wedge the rebuild.

Confirm the source is actually correct before blaming the server, by checking the *production* output:

```bash
npm --prefix <app> run build
grep -rlo "flex:0 1 124px" dist/            # the new declaration, minified
grep -rlo "container-type:inline-size" dist/ # the old one should be gone
```

If `dist/` has the new CSS and the CSSOM has the old, it is the dev server. Restart it — same command,
same port; it is a localhost process and the restart is immediately reversible:

```bash
# find it, then restart with the original command
# Windows: Get-CimInstance Win32_Process -Filter "ProcessId=<pid>" | Select CommandLine
npm --prefix <app> start
```

Expect the restart to also pull in unrelated in-flight edits from other sessions in the same tree.
Re-read what changed on screen before attributing any of it to your own work.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)
