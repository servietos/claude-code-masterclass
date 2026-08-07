# dotnet-cli

Quick reference for .NET CLI commands. Use these instead of editing `.csproj` files directly.

## When to Use

- Building or compiling .NET projects and solutions
- Running unit or integration tests with filtering
- Managing NuGet packages (add, remove, update, restore)
- Formatting and linting C# code with `dotnet format`
- Using hot reload / watch mode during development
- Organizing multi-project solutions
- Troubleshooting build failures and dependency issues
- Publishing applications to a target runtime or folder

## Build

| Command | Description |
|---|---|
| `dotnet build` | Build the project or solution in Debug configuration |
| `dotnet build --configuration Release` | Build in Release configuration |

## Run and Watch

| Command | Description |
|---|---|
| `dotnet run` | Build and run the project |
| `dotnet watch run` | Run with hot reload — restarts on file changes |

## Test

| Command | Description |
|---|---|
| `dotnet test` | Run all tests |
| `dotnet test --filter "ClassName=ItemsControllerTests"` | Run tests matching a class name |
| `dotnet test -v n` | Run tests with normal verbosity output |

## NuGet

| Command | Description |
|---|---|
| `dotnet add package <Name>` | Add a NuGet package reference |
| `dotnet remove package <Name>` | Remove a NuGet package reference |
| `dotnet restore` | Restore all package dependencies |
| `dotnet list package` | List all package references in the project |

## EF Core Migrations

| Command | Description |
|---|---|
| `dotnet ef migrations add <Name>` | Scaffold a new migration |
| `dotnet ef database update` | Apply pending migrations to the database |
| `dotnet ef migrations remove` | Remove the last unapplied migration |

Prefix with `--project <path>` when running from the solution root:

```bash
dotnet ef migrations add AddIndexTable --project src/my-api
dotnet ef database update --project src/my-api
```

## Publish

| Command | Description |
|---|---|
| `dotnet publish -c Release -o ./publish` | Publish to the `./publish` folder in Release configuration |

## Format

| Command | Description |
|---|---|
| `dotnet format` | Format all C# files to match `.editorconfig` rules |

## Solution Management

| Command | Description |
|---|---|
| `dotnet new sln` | Create a new solution file |
| `dotnet sln add <project>` | Add a project to the solution |
| `dotnet sln list` | List all projects in the solution |
