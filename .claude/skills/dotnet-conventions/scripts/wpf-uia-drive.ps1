<#
Drive a WPF desktop app through real mouse/keyboard input and UI Automation, from a JSON step list.
Finds controls by their ToolTip (UIA HelpText), so icon-only toolbars are addressable.
Real input is only sent while a window of the app owns the foreground: when the user is typing in
another window, SetForegroundWindow fails silently and a click would land in that window, so the
step prints BLOCKED and counts as missing instead. Shots use PrintWindow, so a covered window is
still captured as itself.
Reports a crash from the Application event log (.NET Runtime) if the process dies.

  pwsh -NoProfile -File wpf-uia-drive.ps1 -Exe <path.exe> -Steps <steps.json> -Out <dir> [-AppArgs "--x"] [-Attach]

-Attach drives the instance that is already running (process name from -Exe) instead of starting
one, and never stops it: use it for single-instance apps and for the user's own running app, where
a second start only hands off to the first process and exits.

steps.json is an array; coordinates in "drag"/"click" are relative to the anchor element
(set with {"anchor": "<ControlType name, e.g. Image>"}; default: the window's top-left).
A step that needs a window (anchor, press, invoke, pick, minimize, shot, close) before any "window"
step picks the process's first titled top-level window and prints which one it took.
  {"keys": "^+S"}                    send keys: ^ Ctrl, + Shift, % Alt, then one char or {ENTER} {ESC} {TAB}
  {"type": "Hello"}                  type text
  {"screenDrag": [x1,y1,x2,y2]}      drag in absolute screen pixels (e.g. a capture overlay)
  {"window": "Editor title regex"}   wait up to 5 s for a top-level window of the process and make it current
  {"anchor": "Image"}                first descendant of that ControlType becomes the coordinate origin
  {"press": "Undo"}                  click the control whose ToolTip is "Undo" (real mouse input)
  {"invoke": "Undo"}                 invoke it through UIA InvokePattern instead: no mouse, no focus needed;
                                     falls back to the control's Name when no ToolTip matches (sidebar buttons)
  {"pick": ["Thickness", "12"]}      select an item in the ComboBox whose ToolTip is "Thickness"
  {"drag": [x1,y1,x2,y2]}            drag relative to the anchor
  {"click": [x,y]}                   click relative to the anchor
  {"minimize": true}                 minimize the current window; prints whether it is still visible
  {"shot": "name"}                   save the current window as <Out>/<name>.png
  {"sleep": 500}                     wait in ms
  {"close": true}                    close the current window (WindowPattern)
Summary line: steps=N ok=N missing=N crashed=<bool> tooltips=<count>
#>
param(
    [Parameter(Mandatory)][string]$Exe,
    [Parameter(Mandatory)][string]$Steps,
    [Parameter(Mandatory)][string]$Out,
    [string]$AppArgs = '',
    [int]$StartupMs = 3000,
    [switch]$KeepRunning,
    [switch]$Attach
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class UiaInput {
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, uint f, UIntPtr e);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern short VkKeyScan(char c);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr ctx);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
$A = [System.Windows.Automation.AutomationElement]
$T = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
function Cond($prop, $val) { New-Object System.Windows.Automation.PropertyCondition($prop, $val) }
function Tap([byte]$vk, [byte[]]$mods) {
    foreach ($m in $mods) { [UiaInput]::keybd_event($m, 0, 0, [UIntPtr]::Zero) }
    [UiaInput]::keybd_event($vk, 0, 0, [UIntPtr]::Zero); [UiaInput]::keybd_event($vk, 0, 2, [UIntPtr]::Zero)
    foreach ($m in $mods) { [UiaInput]::keybd_event($m, 0, 2, [UIntPtr]::Zero) }
    Start-Sleep -Milliseconds 120
}
function SendKeysSpec([string]$spec) {
    $mods = @(); $i = 0
    while ($i -lt $spec.Length -and '^+%'.Contains($spec[$i])) { $mods += @{ '^' = 0x11; '+' = 0x10; '%' = 0x12 }[[string]$spec[$i]]; $i++ }
    $rest = $spec.Substring($i)
    $named = @{ '{ENTER}' = 0x0D; '{ESC}' = 0x1B; '{TAB}' = 0x09; '{DEL}' = 0x2E }
    if ($named.ContainsKey($rest.ToUpper())) { Tap $named[$rest.ToUpper()] $mods; return }
    Tap ([byte]([UiaInput]::VkKeyScan($rest.ToLower()[0]) -band 0xFF)) $mods
}
function TypeText([string]$text) {
    foreach ($ch in $text.ToCharArray()) {
        $scan = [UiaInput]::VkKeyScan($ch); $mods = @(); if ($scan -band 0x100) { $mods += 0x10 }
        Tap ([byte]($scan -band 0xFF)) $mods
    }
}
function MoveTo($x, $y) { [UiaInput]::SetCursorPos([int]$x, [int]$y) | Out-Null }
function Click($x, $y) { MoveTo $x $y; Start-Sleep -Milliseconds 150; [UiaInput]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero); [UiaInput]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 350 }
function Drag($x1, $y1, $x2, $y2) {
    MoveTo $x1 $y1; Start-Sleep -Milliseconds 150; [UiaInput]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 100
    foreach ($i in 1..12) { MoveTo ($x1 + ($x2 - $x1) * $i / 12) ($y1 + ($y2 - $y1) * $i / 12); Start-Sleep -Milliseconds 30 }
    [UiaInput]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 300
}
function OwnsForeground {
    if ($win) { [UiaInput]::SetForegroundWindow([IntPtr]$win.Current.NativeWindowHandle) | Out-Null; Start-Sleep -Milliseconds 150 }
    $fp = [uint32]0
    [UiaInput]::GetWindowThreadProcessId([UiaInput]::GetForegroundWindow(), [ref]$fp) | Out-Null
    return $fp -eq $p.Id
}
function Center($el) { $r = $el.Current.BoundingRectangle; @([int]($r.X + $r.Width / 2), [int]($r.Y + $r.Height / 2)) }

New-Item -ItemType Directory -Force -Path $Out | Out-Null
$plan = Get-Content $Steps -Raw | ConvertFrom-Json
$started = Get-Date
if ($Attach) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($Exe)
    $p = Get-Process -Name $name -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $p) { "no running '$name' to attach to"; "steps=0 ok=0 missing=0 crashed=False tooltips=0"; exit 1 }
    "attached to $name pid $($p.Id)"
} else {
    $p = if ($AppArgs) { Start-Process $Exe -ArgumentList $AppArgs -PassThru } else { Start-Process $Exe -PassThru }
    Start-Sleep -Milliseconds $StartupMs
}
function AutoWindow {
    foreach ($try in 1..25) {
        $w = $A::RootElement.FindAll($T::Children, (Cond $A::ProcessIdProperty $p.Id)) | Where-Object { $_.Current.Name } | Select-Object -First 1
        if ($w) { return $w }
        Start-Sleep -Milliseconds 200
    }
    return $null
}
$win = $null; $ox = 0; $oy = 0; $ok = 0; $missing = 0; $n = 0; $tipCount = 0

foreach ($s in $plan) {
    $n++
    if ($p.HasExited) { "step $n skipped: process exited"; break }
    $done = $true
    $kind = @($s.PSObject.Properties.Name)[0]
    if (@('keys', 'type', 'screenDrag', 'press', 'drag', 'click') -contains $kind -and -not (OwnsForeground)) {
        "BLOCKED step $n ($kind): another process has the foreground, input not sent"; $missing++; continue
    }
    if (-not $win -and @('anchor', 'press', 'invoke', 'pick', 'minimize', 'shot', 'close') -contains $kind) {
        $win = AutoWindow
        if (-not $win) { "MISSING window for step $n ($kind): no titled window of pid $($p.Id); add a window step"; $missing++; continue }
        $r = $win.Current.BoundingRectangle; $ox = [int]$r.X; $oy = [int]$r.Y
        "window '$($win.Current.Name)' picked automatically (no window step before step $n)"
    }
    switch ($kind) {
        'keys' { SendKeysSpec $s.keys }
        'type' { TypeText $s.type }
        'sleep' { Start-Sleep -Milliseconds $s.sleep }
        'screenDrag' { $d = $s.screenDrag; Drag $d[0] $d[1] $d[2] $d[3] }
        'window' {
            $win = $null
            foreach ($try in 1..25) {
                $all = $A::RootElement.FindAll($T::Children, (Cond $A::ProcessIdProperty $p.Id))
                $win = $all | Where-Object { $_.Current.Name -match $s.window } | Select-Object -First 1
                if ($win) { break }; Start-Sleep -Milliseconds 200
            }
            if ($win) {
                [UiaInput]::SetForegroundWindow([IntPtr]$win.Current.NativeWindowHandle) | Out-Null
                $r = $win.Current.BoundingRectangle; $ox = [int]$r.X; $oy = [int]$r.Y
                $tips = $win.FindAll($T::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | ForEach-Object { $_.Current.HelpText } | Where-Object { $_ }
                $tipCount = @($tips).Count
                "window '$($win.Current.Name)' tooltips: $($tips -join ', ')"
            } else { "MISSING window /$($s.window)/"; $done = $false }
        }
        'anchor' {
            $ct = $CT.GetField($s.anchor).GetValue($null)
            $el = $win.FindFirst($T::Descendants, (Cond $A::ControlTypeProperty $ct))
            if ($el) { $r = $el.Current.BoundingRectangle; $ox = [int]$r.X; $oy = [int]$r.Y; "anchor $($s.anchor) at $ox,$oy size $($r.Width)x$($r.Height)" } else { "MISSING anchor $($s.anchor)"; $done = $false }
        }
        'press' {
            $el = $win.FindFirst($T::Descendants, (Cond $A::HelpTextProperty $s.press))
            if ($el) { $c = Center $el; Click $c[0] $c[1] } else { "MISSING control '$($s.press)'"; $done = $false }
        }
        'invoke' {
            $el = $win.FindFirst($T::Descendants, (Cond $A::HelpTextProperty $s.invoke))
            if (-not $el) { $el = $win.FindFirst($T::Descendants, (New-Object System.Windows.Automation.AndCondition((Cond $A::NameProperty $s.invoke), (Cond $A::IsInvokePatternAvailableProperty $true)))) }
            if ($el) { $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 350 } else { "MISSING control '$($s.invoke)'"; $done = $false }
        }
        'pick' {
            $both = New-Object System.Windows.Automation.AndCondition((Cond $A::HelpTextProperty $s.pick[0]), (Cond $A::ControlTypeProperty $CT::ComboBox))
            $combo = $win.FindFirst($T::Descendants, $both)
            if (-not $combo) { "MISSING combo '$($s.pick[0])'"; $done = $false; break }
            $ec = $combo.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern); $ec.Expand(); Start-Sleep -Milliseconds 400
            $item = $combo.FindFirst($T::Descendants, (Cond $A::NameProperty ([string]$s.pick[1])))
            if ($item) { $item.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select() } else { "MISSING item '$($s.pick[1])' in '$($s.pick[0])'"; $done = $false }
            Start-Sleep -Milliseconds 200; $ec.Collapse(); Start-Sleep -Milliseconds 300
        }
        'drag' { $d = $s.drag; Drag ($ox + $d[0]) ($oy + $d[1]) ($ox + $d[2]) ($oy + $d[3]) }
        'click' { Click ($ox + $s.click[0]) ($oy + $s.click[1]) }
        'minimize' {
            $h = [IntPtr]$win.Current.NativeWindowHandle; [UiaInput]::ShowWindow($h, 6) | Out-Null; Start-Sleep -Milliseconds 800
            "after minimize visible=$([UiaInput]::IsWindowVisible($h))"
        }
        'shot' {
            $h = [IntPtr]$win.Current.NativeWindowHandle
            $dpi = [UiaInput]::SetThreadDpiAwarenessContext([IntPtr]-4)
            $r = New-Object UiaInput+RECT; [UiaInput]::GetWindowRect($h, [ref]$r) | Out-Null
            $bmp = New-Object System.Drawing.Bitmap(($r.R - $r.L), ($r.B - $r.T))
            $g = [System.Drawing.Graphics]::FromImage($bmp); $dc = $g.GetHdc()
            [UiaInput]::PrintWindow($h, $dc, 2) | Out-Null
            $g.ReleaseHdc($dc); $g.Dispose()
            if ($dpi -ne [IntPtr]::Zero) { [UiaInput]::SetThreadDpiAwarenessContext($dpi) | Out-Null }
            $bmp.Save((Join-Path $Out "$($s.shot).png")); $bmp.Dispose()
        }
        'close' { $win.GetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern).Close(); Start-Sleep -Milliseconds 1500 }
        default { "unknown step '$(@($s.PSObject.Properties.Name)[0])'"; $done = $false }
    }
    if ($done) { $ok++ } else { $missing++ }
}

$exited = $p.HasExited
if ($exited) {
    $ev = Get-WinEvent -FilterHashtable @{ LogName = 'Application'; ProviderName = '.NET Runtime'; StartTime = $started } -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($ev) { "CRASH:"; ($ev.Message -split "`n" | Select-Object -First 8) -join "`n" } else { "process exited (no .NET Runtime event)" }
} elseif (-not $KeepRunning -and -not $Attach) {
    Stop-Process -Id $p.Id
}
"steps=$n ok=$ok missing=$missing crashed=$exited tooltips=$tipCount"
