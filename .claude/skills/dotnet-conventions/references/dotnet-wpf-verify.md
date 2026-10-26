# Driving and verifying a WPF app

How to prove a WPF desktop change works in the running app: drive it with real input or UIA, capture
it with PrintWindow, measure margins by ink and compare before and after. The build and the app
conventions live in [`dotnet-wpf-desktop`](dotnet-wpf-desktop.md); unit tests of a single window in
[`dotnet-testing-wpf-windows`](dotnet-testing-wpf-windows.md).

## Drive and capture

- Drive every new tool with real input before calling it done:
  `pwsh -NoProfile -File scripts/wpf-uia-drive.ps1 -Exe <app.exe> -Steps steps.json -Out <dir>`
  (step list format in the script header: hotkeys, screen drags, `window`, `anchor`, `press` by
  tooltip, `invoke` by tooltip or Name, `pick` in a combo, `drag`/`click` relative to the anchor, `minimize`, `shot`, `close`).
  A single-instance app hands a second start to the running process and exits, so add `-Attach`
  to drive the instance already running (it is never stopped); window steps are optional, the
  first titled window of the process is picked when none ran.
  It prints `steps= ok= missing= crashed=` and the `.NET Runtime` event-log stack on a crash; a
  `BLOCKED` line means the user had the foreground and nothing was sent. Shots use `PrintWindow`, so
  they show the app even when another window covers it. Then read what the app persisted (sidecar,
  settings) and the shots, not just the summary.
- Hover, drag and right-click states need real input, so a UIA-only check cannot see them. Drive them
  while the app owns the foreground, or report them as not seen on screen. No UIA pattern opens a
  `ContextMenu`, so a dialog reachable only from a right-click menu cannot be captured UIA-only.
  `InvokePattern` also skips mouse capture and hit testing: a "clicking it does nothing" bug does not
  reproduce through UIA, so report its cause as found in the code, not as observed.
- Margins and before/after: `pwsh -NoProfile -File scripts/wpf-shot-gaps.ps1 -Path <shot or folder>
  -ContentLeft <px> -Top <px> -Bottom <px>` prints the left and right gap to the outermost ink per
  shot (scrollbar thumb ignored) and ends in `files= equal= unequal= maxdiff=`;
  `scripts/wpf-shot-compare.ps1 -Before <png> -After <png> -Out <png>` puts two shots side by side.
- Responsive layouts: resize the window through UIA `TransformPattern.Resize` to its minimum width,
  capture, then restore the old size and position. Between steps use `Start-Sleep -Milliseconds`;
  a bare `Start-Sleep 2500` waits 2500 seconds.
- One agent at a time rebuilds and restarts the app: two drivers stopping and starting the same exe
  kill each other's instance mid-capture. Read-only proposal work can run beside it.
- Launch once with `--autostart` and confirm no main window appears. Test data the run writes into
  the user's own folders is yours to remove: note the ids it created and delete exactly those.

Back to the index: [dotnet-conventions](../SKILL.md)
