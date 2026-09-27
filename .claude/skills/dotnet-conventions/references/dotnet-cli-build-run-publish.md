# dotnet CLI: build, run, watch, publish

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

## Publish

| Command | Description |
|---|---|
| `dotnet publish -c Release -o ./publish` | Publish to the `./publish` folder in Release configuration |

Back to the index: [dotnet-cli](dotnet-cli.md)
