# dotnet-cli

Quick reference for .NET CLI commands. Use these instead of editing `.csproj` files directly.

**Some projects prohibit `dotnet ef` outright.** See the migrations leaf before running any of it.

| You want to... | Read |
|---|---|
| How do I compile, run with hot reload, or publish a project, and what does the dotnet CLI cover at all? | [dotnet-cli-build-run-publish](dotnet-cli-build-run-publish.md) |
| How do I add or list a NuGet package, format C# to .editorconfig, or add a project to a solution? | [dotnet-cli-packages-solutions](dotnet-cli-packages-solutions.md) |
| How do I run or filter tests, see a failure's stack trace, or run the suite while the app is up under dotnet watch? | [dotnet-cli-test](dotnet-cli-test.md) |
| How do I add or apply an EF Core migration, and which repos forbid dotnet ef outright in favour of SQL delta scripts? | [dotnet-cli-ef-migrations](dotnet-cli-ef-migrations.md) |
| Build FAILED with MSB3021/MSB3026/MSB3027, a file is locked by a running app, or I need a compile verdict without killing anyone's process. | [dotnet-cli-build-lock](dotnet-cli-build-lock.md) |
