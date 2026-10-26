# Unit-testing WPF windows and views in xUnit

A WPF bug that lives in a window (where it opens, which cursor it shows, what the wheel does) can be
tested in xUnit without launching the app or touching its single-instance mutex. Five rules make it
reliable.

## The harness

1. **One STA thread and one `Application` per test process.** WPF allows a single `Application`
   per AppDomain, so a lazy static starts one background STA thread, creates
   `new Application { ShutdownMode = ShutdownMode.OnExplicitShutdown }` there, runs
   `Dispatcher.Run()`, and every test marshals its body onto that dispatcher
   (`dispatcher.InvokeAsync(body).Task.Unwrap().GetAwaiter().GetResult()`).
2. **Match the app's DPI awareness.** Call `SetProcessDpiAwarenessContext(-4)` (PerMonitorV2) on
   that thread before the `Application` exists when the app manifest declares PerMonitorV2;
   otherwise `GetWindowRect` returns scaled values and position assertions fail only on a scaled
   monitor.
3. **No parallel tests:** `[assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)]`.
   The tests share one thread, one `Application` and any static override.
4. **Never the real settings file.** Give the settings class an `internal static string?
   FilePathOverride` (plus `InternalsVisibleTo` for the test project) and set it from an
   `IDisposable` fixture that points at a temp folder and deletes it on dispose.
5. **Pack URIs need the app's resource assembly.** In a test process `Application.ResourceAssembly`
   falls back to the test runner and its setter throws, so a window that loads
   `pack://application:,,,/` resources fails with "Cannot locate resource". Set the private field once,
   just before `new Application`:
   `typeof(Application).GetField("_resourceAssembly", BindingFlags.Static | BindingFlags.NonPublic)!.SetValue(null, typeof(App).Assembly);`

```csharp
internal static class Sta
{
    [DllImport("user32.dll")] static extern bool SetProcessDpiAwarenessContext(nint context);
    static readonly Lazy<Dispatcher> Ui = new(() =>
    {
        Dispatcher? d = null; var ready = new ManualResetEventSlim();
        var t = new Thread(() =>
        {
            SetProcessDpiAwarenessContext(-4);
            _ = new Application { ShutdownMode = ShutdownMode.OnExplicitShutdown };
            d = Dispatcher.CurrentDispatcher; ready.Set(); Dispatcher.Run();
        }) { IsBackground = true };
        t.SetApartmentState(ApartmentState.STA); t.Start(); ready.Wait(); return d!;
    });
    public static void Run(Func<Task> body) => Ui.Value.InvokeAsync(body).Task.Unwrap().GetAwaiter().GetResult();
}
```

Settle after `Show()` before asserting: `await Task.Delay(n)` then
`await dispatcher.InvokeAsync(() => { }, DispatcherPriority.ApplicationIdle)`, so layout and
`Loaded` have run. Show windows with `ShowActivated = false` so a run never steals focus.

## Asserting what the user sees

- **Cursor:** hit-test the point (`view.InputHitTest(point)`), raise `Mouse.QueryCursorEvent` on the
  hit element with a `QueryCursorEventArgs`, and assert `args.Cursor`. This is the question WPF asks
  the element under the pointer, so it catches a cursor set on the wrong element of the tree.
  Test both the image and the empty margin around it.
- **Wheel:** raise `UIElement.PreviewMouseWheelEvent` with a `MouseWheelEventArgs` on the host and
  read the zoom transform's `ScaleX`.
- **Position:** move with `SetWindowPos`, close, open a fresh window and compare `GetWindowRect`
  with the spot; pick the spot on the last monitor so it differs from the default.
- **UI-thread stall:** right after the call that opens the window, queue a timestamp with
  `_ = dispatcher.BeginInvoke(DispatcherPriority.Input, ...)` and await it; the elapsed time is how
  long a click would wait. Seed a temp folder big enough for the old code to fail clearly (40 images
  of 3000x1700 took 3.2 s before a thumbnail fix and 0.5 s after).

## Prove the test catches the bug

Run the suite once against a copy of the tree with the fix undone (copy to `%TEMP%`, revert there,
never in the shared checkout). A test that passes on both is a regression guard, not proof of the
fix; report the two counts ("28 pass fixed, 18 fail on the old code").

Keep throwaway diagnostic tests outside the repo (scratchpad or `%TEMP%`): a delete of a scratch
file in the test project can be blocked by a guard and then ships with the suite.

## Verify

`dotnet test <Tests.csproj> -c Release` builds into `bin\Release`, so it runs beside a Debug
instance of the app that locks `bin\Debug`. Windows flash briefly during the run; that is expected.
