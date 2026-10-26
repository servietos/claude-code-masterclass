# NuGet restore failures: NU1605 downgrade and NU190x vulnerabilities

Two restore diagnostics that appear with no edit in the repo: a floating package released a new
patch, or an advisory was published against something a dependency pulls in. Both are fixed in the
`.csproj` through the CLI, never by suppressing the code.

## NU1605: a floating parent outruns a pinned child

```text
error NU1605: Warning As Error: Detected package downgrade: Microsoft.OpenApi from 2.12.2 to 2.12.0.
   App -> Microsoft.AspNetCore.OpenApi 10.0.13 -> Microsoft.OpenApi (>= 2.12.2 && < 3.0.0)
   App -> Microsoft.OpenApi (>= 2.12.0)
```

The project floats one package (`Microsoft.AspNetCore.OpenApi` at `Version="10.0.*"`) and pins a
package that one depends on (`Microsoft.OpenApi` at `Version="2.12.0"`). A new patch of the floating
parent raises the child's lower bound past the pin, and the next restore fails. The SDK treats NU1605
as an error by default, so `dotnet watch` reports "Failed to build project" although nothing was
compiled.

1. Read the two chain lines. The first names the package that needs more and the minimum it needs.
2. Raise the direct pin to exactly that minimum:
   `dotnet add <proj> package Microsoft.OpenApi --version 2.12.2`. Do not lower or pin the floating
   parent to dodge it, and never add NU1605 to `NoWarn`.
3. Grep every project in the solution for the same pair before calling it done; each one that floats
   the parent and pins the child fails the same way on its next restore:
   `grep -rn 'Include="Microsoft.OpenApi"' --include=*.csproj src/`.

A direct reference set BELOW a transitive minimum is a downgrade by definition, which is why the same
error can come back later from a pin added for the vulnerability fix below.

## NU1902, NU1903, NU1904: a vulnerable transitive package

```text
warning NU1903: Package 'System.Security.Cryptography.Pkcs' 10.0.7 has a known high severity
vulnerability, https://github.com/advisories/GHSA-846f-f764-76mx
```

1. Find who brings it in: `dotnet nuget why <proj> System.Security.Cryptography.Pkcs`. In the worked
   case it arrived twice, through `Microsoft.Data.SqlClient` (under
   `Microsoft.EntityFrameworkCore.SqlServer`) and through `Microsoft.Identity.Web.TokenCache` (under
   `Microsoft.Identity.Web`).
2. Find the lowest patched version from the advisory URL in the warning (its "Patched versions"
   field, per affected range), one advisory per warning line. Both Pkcs advisories were fixed in
   10.0.13 for the 10.x line.
3. Prefer bumping the parent, on the same major, when a release of it already brings the patched
   version. Otherwise add a direct reference:
   `dotnet add <proj> package System.Security.Cryptography.Pkcs --version 10.0.13`. NuGet's
   nearest-wins rule makes it beat every transitive path. Bumping EF Core, ASP.NET and
   Identity.Web to 10.0.13 or 4.16.1 did not lift Pkcs or `System.Security.Cryptography.Xml`
   (still 10.0.10 in five repos, 2026-10-24); the direct reference did, Xml only in the test
   project that pulled it.
   Under `TreatWarningsAsErrors` the NU190x warnings are restore errors, so the restore and every
   `dotnet list package` fail before printing a table: read the advisories from the error lines.
4. Never silence the warning with `NoWarn`, `NuGetAudit=false` or a lowered `NuGetAuditLevel`.

## Verify

- `dotnet restore <proj> --force` prints no NU1605 and no NU190x line. `--force` makes it a real
  restore, so the audit runs again instead of replaying the last cached result.
- `dotnet list <proj> package --vulnerable --include-transitive` prints "has no vulnerable packages".
- While `dotnet watch run` or the app itself runs for that project, verify with restore only:
  restore writes `obj/` and leaves `bin/` alone, while `dotnet build` fights the running process for
  its output (see [dotnet-cli-build-lock](dotnet-cli-build-lock.md)). The `.csproj` edit retriggers
  `dotnet watch`; Ctrl+R forces it when it sits on the failed state.

Back to the index: [dotnet-cli](dotnet-cli.md)
