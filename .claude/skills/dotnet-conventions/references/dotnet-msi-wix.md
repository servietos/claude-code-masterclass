# Signed MSI installer with the WiX 6 SDK

Package a self-contained .NET desktop app as a per-machine MSI that builds with `dotnet build`,
installs nothing globally, signs the exe and the MSI, offers an optional install-time setting, and can
open on a branded picture screen.

## Project

```xml
<Project Sdk="WixToolset.Sdk/6.0.2">
  <PropertyGroup>
    <OutputName>App</OutputName>
    <Platform Condition="'$(Platform)' == ''">x64</Platform>
    <PublishDir>$(MSBuildProjectDirectory)\obj\publish\</PublishDir>
    <DefineConstants>$(DefineConstants);PublishDir=$(PublishDir)</DefineConstants>
  </PropertyGroup>
  <Target Name="PublishApp" BeforeTargets="BeforeBuild">
    <RemoveDir Directories="$(PublishDir)" />
    <Exec Command="dotnet publish &quot;..\App\App.csproj&quot; -c Release -r win-x64 --self-contained true -o &quot;$(PublishDir)&quot;" />
  </Target>
</Project>
```

`Package.wxs` harvests the publish folder with `<Files Include="$(PublishDir)**" Directory="INSTALLFOLDER" />`,
sets `Scope="perMachine"`, a fixed `UpgradeCode` with `<MajorUpgrade>`, and `<MediaTemplate EmbedCab="yes" />`
for a single-file MSI. Branding: `Manufacturer`, an `<Icon>` plus `ARPPRODUCTICON`, `ARPURLINFOABOUT`
and `ARPHELPLINK`. WiX 6 and later fall under the Open Source Maintenance Fee for revenue-generating
use; say so once to the owner before shipping commercially.

- A Start Menu shortcut in a per-machine package needs its own component under `ProgramMenuFolder`
  keyed on an HKCU registry value (`KeyPath="yes"`), or ICE43/ICE57 fail the build.
- Self-contained WPF is about 50 MB; adding Windows Forms (for a tray icon) adds about 10 MB.

## Versioning

The version lives in the source, in two places with the same semantic value: the app csproj's
`<Version>` (assembly and file version) and the wixproj default
`<AppVersion Condition="'$(AppVersion)' == ''">x.y.z</AppVersion>`, which the publish step passes as
`-p:Version=$(AppVersion)` and `Package.wxs` uses as `Version="$(AppVersion)"`. Release tags are
`v<major>.<minor>.<patch>`; a CI build may pass `-p:AppVersion=` derived from the tag, a local build never does.

- Bump before every MSI build that ships a change, without asking: fix = patch, feature = minor,
  breaking = major. The owner tests the installed app, not the source.
- A rebuilt MSI with an unchanged version does not upgrade: `<MajorUpgrade>` skips an installed
  product of the same version, so the new MSI registers a second product beside the old one, and
  Windows Installer keeps the existing files whose file version is equal. The app then runs old code
  after a "successful" reinstall. Two entries of the same name and version under the `Uninstall`
  registry keys are the symptom; the next higher version removes both. Do not paper over it with
  `AllowSameVersionUpgrades`.
- When the installed app lacks something the build has, check before debugging code:
  `scripts/msi-installed-check.ps1 -ProductName <name> -InstallDir <Program Files folder> -BuildDir <publish folder>`
  reads the `Uninstall` keys and hashes the installed files against the build, and ends in
  `products= duplicates= compared= differing= missing= verdict=current|stale|duplicate|not-installed`.

## Install dialog without a license page

Stock WixUI sets all show a license agreement. Author a small set on `WixUI_Common`
(`WixToolset.UI.wixext` at the same version): Welcome, one custom `OptionsDlg`, `VerifyReadyDlg`,
progress, `ExitDialog`, plus the `DialogRef`s for `FatalError`, `UserExit`, `ErrorDlg`,
`FilesInUse`, `MsiRMFilesInUse`, `PrepareDlg`, and `Publish` rows wiring Next/Back between them.

An opt-in checkbox drives a conditional component, and silent installs pass the same property:

```xml
<Property Id="AUTOSTART" Secure="yes" />
<Component Id="AutostartComponent" Directory="INSTALLFOLDER" Bitness="always64" Condition="AUTOSTART = &quot;1&quot;">
  <RegistryValue Root="HKCU" Key="Software\Microsoft\Windows\CurrentVersion\Run" Name="App" Type="string"
                 Value="&quot;[INSTALLFOLDER]App.exe&quot; --autostart" KeyPath="yes" />
</Component>
```

`msiexec /i App.msi AUTOSTART=1`. In a per-machine package HKCU is the installing user's hive. The data
must match what the app itself writes ([`dotnet-wpf-desktop`](dotnet-wpf-desktop.md)).

## A picture-first first screen

An MSI dialog shows a bitmap plus native controls and nothing else: buttons stay grey and a
`CheckBox` has no transparent background. A branded first screen therefore paints its scene and copy
into one bitmap, and a wording change later means re-rendering that bitmap, not editing the `.wxs`.

- One `Bitmap` control covers the dialog above a bottom line; the checkbox and the buttons sit in the
  grey strip below it. A dialog larger than the stock 370 x 270 units keeps painted text readable.
- Draw the bitmap at twice its 96 dpi size (one dialog unit is about 1.333 px at 96 dpi): MSI scales
  dialogs with the display, so a 1x bitmap blurs at 150 percent. Render it from a scratch HTML page
  (web fonts the installer cannot ship) with `scripts/render-msi-bitmap.ps1 -Html <page> -Width <1x px>
  -Height <1x px> -Out <Assets\x.bmp>`; it prints `bitmap= width= height= bpp=24 bytes=`.
- Replace `WelcomeDlg` (and an options dialog) for a fresh install, keep the stock one for patches:

```xml
<InstallUISequence>
  <Show Dialog="StartDlg" Before="ProgressDlg" Condition="NOT Installed" />
  <Show Dialog="override WelcomeDlg" Before="ProgressDlg" Condition="Installed AND PATCH" />
</InstallUISequence>
```

- An Install button on that screen gets `ElevationShield="yes"`, the dialog `TrackDiskSpace="yes"`,
  and a copy of `VerifyReadyDlg`'s Install publishes:

```xml
<Control Id="Install" Type="PushButton" X="370" Y="299" Width="80" Height="17" Default="yes" ElevationShield="yes" Text="!(loc.VerifyReadyDlgInstall)">
  <Publish Event="EndDialog" Value="Return" Order="1" Condition="OutOfDiskSpace &lt;&gt; 1" />
  <Publish Event="SpawnDialog" Value="OutOfRbDiskDlg" Order="2" Condition="OutOfDiskSpace = 1 AND OutOfNoRbDiskSpace = 0 AND (PROMPTROLLBACKCOST=&quot;P&quot; OR NOT PROMPTROLLBACKCOST)" />
  <Publish Event="EndDialog" Value="Return" Order="3" Condition="OutOfDiskSpace = 1 AND OutOfNoRbDiskSpace = 0 AND PROMPTROLLBACKCOST=&quot;D&quot;" />
  <Publish Event="EnableRollback" Value="False" Order="4" Condition="OutOfDiskSpace = 1 AND OutOfNoRbDiskSpace = 0 AND PROMPTROLLBACKCOST=&quot;D&quot;" />
  <Publish Event="SpawnDialog" Value="OutOfDiskDlg" Order="5" Condition="(OutOfDiskSpace = 1 AND OutOfNoRbDiskSpace = 1) OR (OutOfDiskSpace = 1 AND PROMPTROLLBACKCOST=&quot;F&quot;)" />
</Control>
```
- `WixUIDialogBmp` is shared by `WelcomeDlg`, `ExitDialog`, `UserExit`, `FatalError` and `PrepareDlg`.
  To restyle only some of them, add a `<Binary Id="ExitDlgBmp" SourceFile="Assets\exit.bmp" />` and
  override their bitmap strings in a project `Strings.en-us.wxl`, leaving `dialog.bmp` alone:

```xml
<WixLocalization Culture="en-us" xmlns="http://wixtoolset.org/schemas/v4/wxl">
  <String Id="ExitDialogBitmap" Value="ExitDlgBmp" />
  <String Id="UserExitBitmap" Value="ExitDlgBmp" />
</WixLocalization>
```

## Signing without signtool

No Windows SDK needed: `Set-AuthenticodeSignature` (pwsh 7) signs PE files and MSIs.

```powershell
$c = Get-Item "Cert:\CurrentUser\My\$env:SIGN_THUMBPRINT"
$r = Set-AuthenticodeSignature -FilePath $env:SIGN_FILE -Certificate $c -HashAlgorithm SHA256 -TimestampServer http://timestamp.digicert.com
if (-not $r.SignerCertificate -or -not $r.TimeStamperCertificate) { throw "Signing failed: $($r.StatusMessage)" }
```

- Sign the published exe `AfterTargets="PublishApp"` (before harvesting) and the MSI `AfterTargets="Build"`
  (`$(TargetPath)`). Pass values through `Exec EnvironmentVariables`, not string interpolation.
- Keep the thumbprint in an overridable property (`-p:SignThumbprint=...`). When the certificate is
  not in the builder's store, print a high-importance message and build unsigned, so other machines
  still build.
- Copy the signed MSI to a stable folder (`AfterTargets="SignMsi"`, a `<Copy>` to `<repo>\setup`).

## "Unknown publisher" and a self-signed certificate

Only a certificate Windows trusts removes the warning: Azure Trusted Signing, a CA-issued code-signing
certificate (key on hardware or a cloud HSM), or a self-signed one trusted per machine.

```powershell
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=example.com, O=Example Ltd, C=AT" `
  -CertStoreLocation Cert:\CurrentUser\My -KeyAlgorithm RSA -KeyLength 3072 -HashAlgorithm SHA256 -NotAfter (Get-Date).AddYears(5)
Export-Certificate -Cert $cert -FilePath certs\codesigning.cer -Type CERT   # public part only, goes in the repo
```

Each machine that should trust it imports the `.cer` (elevated) into `Cert:\LocalMachine\Root` and
`Cert:\LocalMachine\TrustedPublisher` (`Import-Certificate`), or receives it via Intune or Group Policy.
The private key never enters the repo; whoever holds it can sign anything those machines trust.

## Verify

- `dotnet build -c Release` of the wixproj: 0 warnings, 0 errors, ICE validation included.
- `Get-AuthenticodeSignature <msi>`: `Valid` on a machine that trusts the certificate, `UnknownError`
  elsewhere (expected for self-signed), with a non-null `TimeStamperCertificate`.
- Read the MSI tables (`Registry`, `Component`, `Control`, `Property`) through the
  `WindowsInstaller.Installer` COM object instead of installing to inspect them. `ExitDialog` appears
  only after a real install: check its `Control` row and `Binary` entry and render the bitmap offline.
- Never query `Win32_Product` (`Get-CimInstance Win32_Product`, `wmic product`) to learn what is
  installed: it runs a consistency check that reconfigures every installed MSI product on the machine.
  Read the `Uninstall` registry keys and the install folder instead.
- To look at a dialog without installing, start `msiexec /i`, capture it, then close it through UI
  Automation (Invoke Cancel, Yes, Finish), all in ONE script: in one session msiexec windows started in
  one tool call were gone by the next. Never invoke Install.
- `PrintWindow` returns an MSI `Bitmap` control blank. Copy the dialog's window rectangle from the
  screen instead, only while `GetForegroundWindow` is that dialog, or the grab shows whatever covers it
  (the foreground rule in [`dotnet-wpf-desktop`](dotnet-wpf-desktop.md)).

Back to the index: [dotnet-conventions](../SKILL.md)
