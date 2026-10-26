# WPF desktop utilities: tray icon, autostart, click-through overlay, sign-in popup

For a small WPF tool that lives in the system tray, starts with Windows and draws over the desktop.
Proven on a .NET 10 screen-annotation app (overlay per monitor, toolbar, tray menu, autostart).

## Tray icon in a WPF project

WPF has no tray icon; use the Windows Forms `NotifyIcon`. Turning on `UseWindowsForms` next to
`UseWPF` breaks a project that uses `ImplicitUsings`: every file fails with CS0104 (`Application`,
`Color`, `Brush`, `Button`, `Point`, `TextBox`, `KeyEventArgs`, `MouseEventArgs` are ambiguous).
Remove the two implicit namespaces and alias Forms where it is used:

```xml
<UseWPF>true</UseWPF>
<UseWindowsForms>true</UseWindowsForms>
<!-- WPF app: per-monitor DPI comes from app.manifest; the WinForms analyzer does not apply -->
<NoWarn>$(NoWarn);WFO0003</NoWarn>
...
<ItemGroup>
  <Using Remove="System.Windows.Forms" />
  <Using Remove="System.Drawing" />
</ItemGroup>
```

```csharp
using Forms = System.Windows.Forms;
using var stream = System.Windows.Application.GetResourceStream(new Uri("pack://application:,,,/Assets/App.ico")).Stream;
var icon = new Forms.NotifyIcon { Icon = new System.Drawing.Icon(stream), Text = "App", ContextMenuStrip = menu, Visible = true };
```

- `WFO0003` appears the moment `UseWindowsForms` is on and `app.manifest` declares DPI awareness.
  Its advice (`Application.SetHighDpiMode`) is a WinForms API; in a WPF app keep the manifest and
  suppress the analyzer with the comment above. With `TreatWarningsAsErrors` it otherwise fails the build.
- Dispose the `NotifyIcon` in `App.OnExit` (`Visible = false; Dispose()`), or a ghost icon stays in
  the tray until the mouse passes over it.
- Set `ShutdownMode="OnExplicitShutdown"` in `App.xaml` when the main window can be hidden, and exit
  only through an explicit Exit/Close (`Application.Current.Shutdown()`).
- Hiding the toolbar from the tray must leave the app usable: switch any input-capturing mode off
  first (for an overlay, back to click-through).

## Autostart, minimized only when Windows starts it

- Write `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, value name = the app name, data
  `"<Environment.ProcessPath>" --autostart`. Remove it with `DeleteValue(name, throwOnMissingValue: false)`.
- In `OnStartup`, show the main window unless `e.Args.Contains("--autostart")`; the tray icon is the
  way back in. A normal launch always shows the full UI.
- A window the autostart launch keeps hidden stays hidden when another feature moves or docks it, and
  any panel it hosts disappears with it. Every path that needs it on screen calls `Show()` with
  `ShowActivated = false` first; test that path with a window that was never shown.
- The option's state IS the registry value: read it for the checkbox, never mirror it in a settings file.
- An installer that offers the same option must write byte-identical data (see
  [`dotnet-msi-wix`](dotnet-msi-wix.md)), so the app's toggle recognises and can remove it.

## Minimize to tray

- On `StateChanged` with `WindowState.Minimized`, `Hide()` the window and keep it in a list; a tray
  left-click (double-click can keep its own action) restores every hidden window: `Show()`, set
  `WindowState.Normal`, `Activate()`. Any existing "bring to front" path must go through the same
  restore, or it activates a hidden window that never appears.

## Transparent, click-through overlay per monitor

- One window per monitor (`EnumDisplayMonitors` + `GetMonitorInfo.rcMonitor`), `WindowStyle=None`,
  `AllowsTransparency=True`, `Topmost=True`, `ShowInTaskbar=False`; place it with `SetWindowPos`
  in physical pixels on `SourceInitialized`, with `PerMonitorV2` in `app.manifest`.
- A fully transparent background lets clicks fall through a layered window. While the overlay must
  catch input, give its surface a near-transparent brush (`#01000000`).
- Click-through: add `WS_EX_TRANSPARENT` (keep `WS_EX_LAYERED`) with `GetWindowLongPtr` /
  `SetWindowLongPtr(GWL_EXSTYLE)`; remove it to capture input again. Drawings stay visible either way.
- `GetWindowLongPtr` exists only in 64-bit user32: set `<PlatformTarget>x64</PlatformTarget>`.
- Re-raise the toolbar above the overlays when an overlay activates (`Topmost = false; Topmost = true`).

## A list with columns (Fluent theme)

- Restyle rows through the `ListViewItem` template. Fluent paints hover and selection on its own
  template part, so a `Background`/`Foreground` set by a DataTrigger loses on hover: a white-on-accent
  "now playing" row turned light grey under white text. Give the `ItemContainerStyle` a
  `ControlTemplate` (a `Border` bound to `Background` and `Padding`) and order the triggers hover,
  selected, state, then state plus hover (`MultiDataTrigger` with
  `{Binding IsMouseOver, RelativeSource={RelativeSource Self}}`); the last matching trigger wins.

```xml
<Setter Property="Template">
  <Setter.Value>
    <ControlTemplate TargetType="ListViewItem">
      <Border Background="{TemplateBinding Background}" CornerRadius="4" Margin="0,1" Padding="{TemplateBinding Padding}">
        <ContentPresenter HorizontalAlignment="{TemplateBinding HorizontalContentAlignment}" VerticalAlignment="Center" />
      </Border>
    </ControlTemplate>
  </Setter.Value>
</Setter>
```

- Resizable columns: a header `Grid` above the list whose `ColumnDefinition.Width` binds `TwoWay` to
  star `GridLength` properties on the view model, a `GridSplitter` with
  `ResizeBehavior="CurrentAndNext"` in the header, and every row's `ColumnDefinition` bound `OneWay` to
  `{Binding DataContext.TitleWidth, RelativeSource={RelativeSource AncestorType=ListView}}`. Star
  widths keep the list filling its width; match the header margin to the row padding in DIPs.
- Hide a column with width 0 and collapse its content too: a `Grid` does not clip, so a `TextBlock`
  with a margin in a 0-width column paints over its neighbour. Toggle columns from a `ContextMenu`
  of `IsCheckable` items bound to bool properties; one menu resource with `x:Shared="False"` serves
  both the header and the list.
- Hairline divider: a `GridSplitter` fills its whole width with `Background`, so a thin line needs a
  template: a transparent 9 px hit area with a centered 1 px `Border` that turns accent on
  `IsMouseOver` and `IsDragging`. In the rows draw a 1 px `Border` at the same offset with a negative
  vertical margin equal to the row padding plus margin, so the line runs unbroken through the list.
- Full text only when cut off: bind the cell's `ToolTip` to its own `Text` and set `e.Handled = true`
  in `ToolTipOpening` unless `new FormattedText(...).WidthIncludingTrailingWhitespace` exceeds
  `ActualWidth`. A wrapped text clamped by `MaxHeight` (a three-line title) is cut off by height:
  set the `FormattedText`'s `MaxTextWidth` to `ActualWidth` and copy `LineHeight`, then compare its
  `Height` with `ActualHeight`; the width test never fires for it.
- Implicit `ScrollBar` and `ToolTip` styles in application resources reach inside the Fluent
  `ScrollViewer` and `ListView` templates: one `ScrollBar` style whose `Track` thumb draws a 4 px bar
  in a 10 px hit area restyles every scrollbar in the app.

## Page layout: equal margins and responsive columns

- One page margin, defined once: a `Thickness` resource (`PageMargin`) that every page grid uses,
  never the same numbers typed per view.
- Keep the scrollbar inside the right margin, or the right gap reads one scrollbar wider than the
  left: give the `ScrollViewer` or `ListView` `Margin="0,0,-W,0"` (W = the scrollbar's width, also a
  resource) and its content a right inset of W. Header actions outside the scroller (Save, icon
  actions) then end on the same right edge as the fields below them.
- Two columns that collapse to one: a uniform adaptive panel (columns = `(width + spacing) /
  (minItem + spacing)`, item width capped at `MaxItemWidth`) when every cell is one line; a masonry
  panel that puts each child into the shortest column when blocks differ in height, because a
  uniform grid stretches each row to its tallest cell and leaves gaps. A lone card fills the row only
  when `MaxItemWidth` is larger than the content width.
- A hero image that scales with the window: a `Viewbox Stretch="Uniform"` in a star column, with no
  `ScrollViewer` around it (the `Viewbox` needs a finite height to scale against).
- Measure margins in the screenshot, to the outermost ink, left and right gap in px: an icon glyph
  sits about 10 DIP inside a 36 DIP icon button, and a button template's transparent 2 DIP border
  insets the visible fill, so equal layout margins can still look unequal.

## In-app sign-in popup (WebView2)

For an app that signs in to a website account without the system browser: a `Window` hosting
`Microsoft.Web.WebView2.Wpf.WebView2`, done when a cookie appears, when the page navigates to a
redirect URI, or when its address matches a pattern. Proven on a .NET 10 speaker controller (SoundCloud web token, Spotify PKCE redirect).

- Give the popup its own profile: `CoreWebView2Environment.CreateAsync(null, <LocalAppData>\<App>\WebView2)`,
  then `await browser.EnsureCoreWebView2Async(environment)` before setting `Source`.
  `WebView2RuntimeNotFoundException` means the runtime is missing: tell the user to install it.
- Cookie capture: read `CoreWebView2.CookieManager.GetCookiesAsync(siteUrl)` when the page opens, on
  every `NavigationCompleted` AND on a 1 s `DispatcherTimer`. A single-page sign-in sets its token
  cookie without a top-level navigation, so a navigation-only check never fires.
- Redirect capture (OAuth code flow): in `NavigationStarting`, when `e.Uri` starts with the redirect
  URI, set `e.Cancel = true` and return the URL; read `code`, `state` and `error` from its query.
  Nothing listens on the loopback port, but the URI must still match the one registered with the provider.
- Address capture: a single-page site (a developer dashboard) reaches its result page through history
  navigation that `NavigationStarting` never reports. Match `CoreWebView2.Source` against a regex with
  a named group on `SourceChanged`, `HistoryChanged` and the 1 s timer as well.
- Set prerequisites up inside the flow: when sign-in needs a value the user must first create on the
  provider's site (an OAuth client ID), Connect opens that site's create page in the same popup with a
  strip above the page (instructions, the redirect URI in a read-only box, a Copy button), captures the
  new ID from the address, saves it and continues into the sign-in. Never send the user to a settings
  field to paste a value the popup can read; keep the field as a fallback.
- Never close the window inside a WebView2 event handler: `Close()` there runs `Closed`, which
  disposes the browser while its own callback is still on the stack. Set the `TaskCompletionSource`
  result first, then `Dispatcher.BeginInvoke(Close)`.

```csharp
browser.CoreWebView2.NavigationStarting += (_, e) =>
{
    if (e.Uri.StartsWith(redirect.AbsoluteUri, StringComparison.OrdinalIgnoreCase))
    {
        e.Cancel = true;
        if (completion.TrySetResult(new Uri(e.Uri))) Dispatcher.BeginInvoke(Close);
    }
};
Closed += (_, _) => { timer.Stop(); browser.Dispose(); completion.TrySetResult(null); };
```
- Size it like a browser: at 520 x 740 DIPs a desktop-only sign-in page cut its form off behind a
  horizontal scrollbar. Open at about 1000 x 800 DIPs, clamped to 95 percent of the owner monitor's
  work area, and keep it resizable.
- Sign-out without a visible window: cookies are reachable only through a browser instance, so host
  one in a 1 px window off-screen (`Left = -10000`, `ShowInTaskbar = false`, `ShowActivated = false`),
  delete every cookie whose `Domain` (leading dot trimmed) is the host or ends with `.<host>`, then
  dispose the browser and close the host.
- Google blocks sign-in inside embedded browsers ("This browser or app may not be secure"): a Google
  account (YouTube) keeps the system browser or browser cookies. Never spoof the user agent to get past it.
- Keep library code UI-free: the core project holds an interface such as
  `Task<Result?> SignInAsync(Request, CancellationToken)` (null when the user closed the window), the
  WPF project implements it and marshals every call to `Application.Current.Dispatcher`.
- Verify: open the popup through a UIA-invoked Connect, capture it with `PrintWindow` and check the
  whole form shows with no horizontal scrollbar, then close it with UIA `WindowPattern.Close` and
  confirm the app treats that as cancelled, not as an error. The user types the credentials.

## Gotchas

- Icon-font glyphs (Segoe MDL2 ``): shell heredocs, `sed` and editors rewrite the escape into the
  literal private-use character or strip the backslash. In XAML use `&#xE70E;`; in C# check the bytes
  with `od -c` (`356 234 215` is U+E70D) rather than trusting what the terminal shows.
- A running instance locks `bin\Debug\...\App.exe`; never kill the user's instance to rebuild.
  Build Release (or the installer's publish) to compile-check instead.
- Replacing a child by index (`canvas.Children[i] = next`) throws `ArgumentException: Specified
  index is already in use` on the first mouse move and kills the process. Use `RemoveAt(i)` then
  `Insert(i, next)`.
- A tool cursor belongs on the whole drawing host, not on the image layer: inside a `DownOnly`
  `Viewbox` a small image leaves a large margin whose hit element has no `Cursor`, so most of the
  area shows the arrow. The same margin fails an `IsMouseOver` guard on the image (wheel zoom dead).
- A remembered window position saved only after `DragMove` misses every other move; save the real
  window rect in `Closing` too, and while docked to another window save the pre-dock spot instead.
- A live draft re-created under the cursor (polygon preview, rubber band) must be
  `IsHitTestVisible = false`: otherwise the next click lands on an element that `MouseMove`
  removes before the event routes, the canvas handler never fires and the click is lost.
- Give icon-only buttons a `ToolTip`: it is the UIA `HelpText`, the handle a test driver clicks by.
- A command that cannot act must say why: toast the returned status message instead of returning
  quietly. A switch (on/off `Button`) does its whole job alone: never disable it through `CanExecute`
  while a menu item doing the same has no guard, and never nest it inside another `Button` (a nav row);
  put both in a `Grid` as siblings. Rows with an on/off state sort live, on first and off last, the
  original order kept in each part, through `ObservableCollection.Move` on every state change.
- Real input reaches the app only while it owns the foreground. When the user is typing elsewhere,
  `SetForegroundWindow` fails without an error and `mouse_event` clicks whatever window is on top:
  one verification double-click landed in the user's terminal. The drive script therefore refuses
  input steps (`BLOCKED`) unless the foreground window belongs to the app; use `invoke` (UIA
  `InvokePattern`) for buttons and keep real input for what only real input can test.
- `Process.MainWindowHandle` can be the app's ToolTip `Popup`, not its window. Find the window among
  `AutomationElement.RootElement` children by `ProcessId` and `Name`, as the `window` step does.
- Screenshots and UIA rectangles are physical pixels; XAML sizes are DIPs. At 150 percent scaling a
  465 px pane is 310 DIP, so divide by the scale before comparing a screenshot with a `MinWidth`.
  A DPI-unaware probe (PowerShell's `Screen.AllScreens`) reports logical monitor bounds, so a saved
  physical-pixel window spot looks off-screen when it is not; read the bounds DPI-aware first.
- A gallery that builds every tile from a full `BitmapImage` decode on the UI thread gets slower with
  each image the user adds (about 80 ms per 3000 px shot, 20 s at 264 shots), and the decodes pile up
  as native WIC memory a small managed heap rarely collects (1.3 GB private bytes, 3.6 MB managed).
  Decode tiles with `DecodePixelWidth`, fill them one at a time at `DispatcherPriority.Background`
  after the window shows, and keep the thumbnail cache static so a reopened window reuses it.
- PowerShell passes `$null` to a P/Invoke `string` parameter as `""`: use `[NullString]::Value`
  (`FindWindow([NullString]::Value, 'Title')`).
- A property `Trigger` on `Tag` (type `object`) with `Value="True"` compares a bound `bool` with the
  string `"True"` and never fires; the build is clean and the control just stays in its off look.
  Give the trigger a real boolean:
  `<Trigger Property="Tag"><Trigger.Value><sys:Boolean>True</sys:Boolean></Trigger.Value>`, with
  `xmlns:sys="clr-namespace:System;assembly=System.Runtime"`. Only a screenshot caught it.
- `BasedOn="{StaticResource Base}"` resolves in file order: a style declared above its base in a
  `ResourceDictionary` builds clean and throws "Cannot find resource" when the page loads. Declare
  every keyed style below its base and open the page before reporting.
- WPF's `TextBox` has no placeholder. Put a `TextBlock` in the same grid cell with
  `IsHitTestVisible="False"`, a left margin matching the box's text inset, and `Visibility` bound
  to the text through a null-or-empty-to-visibility converter; it hides on the first character.

```xml
<TextBox Text="{Binding Url, UpdateSourceTrigger=PropertyChanged}" AutomationProperties.Name="Playlist URL" />
<TextBlock Text="Add playlist by URL" IsHitTestVisible="False" VerticalAlignment="Center" Margin="11,0,0,0"
           Visibility="{Binding Url, Converter={StaticResource NullToVisibility}}" />
```

## Verify

- `dotnet build` with `TreatWarningsAsErrors` reports 0 warnings, 0 errors. A clean build says
  nothing about input handling: both bugs above built clean and only showed up when driven.
- Drive the UI, measure margins and compare shots as [`dotnet-wpf-verify`](dotnet-wpf-verify.md) says.

Back to the index: [dotnet-conventions](../SKILL.md)
