# CLAUDE.md

## Architecture

Controllers go in `Controllers/`, models in `Models/`, one file per class. The namespace matches the folder: `TodoApi.Controllers`, `TodoApi.Models`. Keep `Program.cs` to service registration only.

## Conventions

Return `ProblemDetails` for every error, using the `Problem()` helper in controllers. Use 4xx for client errors and 5xx for server errors. Every list endpoint returns `PaginatedResponse<T>`.

## Secrets

`appsettings.Secrets.json` holds connection strings and API keys. Never read it, never echo it, and never copy its values into another file.

## Build and Run

```bash
dotnet restore
dotnet build
dotnet run
```
