# Test the HR MCP Server with the Inspector

This folder is the completed reference for the starter at `hr-mcp-server/`.

## Prerequisites

- .NET SDK 10.0 or later (`dotnet --version`)
- Node.js, only for the MCP Inspector step

## Run the server

```powershell
cd demos/04-mcp/02-mcp/hr-mcp-server-solution
dotnet run
```

The first start creates `hr.db` through `EnsureCreatedAsync()` and seeds eight employees, then Kestrel reports `Now listening on: http://[::]:47002`. A plain browser GET on that address answers HTTP 400 with an `Mcp-Session-Id header is required` error, which is the expected MCP response to a non-MCP request.

## Connect with MCP Inspector

1. Leave `dotnet run` going in one terminal.
2. In a second terminal, launch the inspector with the provided config:

   ```powershell
   cd demos/04-mcp/02-mcp/hr-mcp-server-solution
   npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp
   ```

The config at `inspector.config.json` tells the inspector to use the HR MCP server's Streamable HTTP base URL `http://localhost:47002`, matching the endpoint that `app.MapMcp()` exposes at the server root (no `/mcp` suffix). This satisfies the newer CLI requirement that `--server` reference an entry in a config file.

### Remote deployment (optional)

After you publish the server to your own App Service, put its hostname into the `hr-mcp-azure-dev` entry of `inspector.config.json` and select that entry:

```powershell
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp-azure-dev
```

The URL shipped in that entry points at an App Service that is no longer deployed, so replace it with your own hostname before running the command.

> **Heads-up:** Updating `inspector.config.json` is a local workflow change only: you do not need to republish the App Service after editing this file. Republish the .NET app itself only when the server code or the configuration inside the deployed artifact changes.

## Smoke Test

Verify the running server is operational:

1. Confirm in the browser inspector that all **6 tools** are listed and accessible:
   - `list_employees`: retrieves all employees ordered by last name
   - `add_employee`: adds a new employee with optional languages and skills
   - `update_employee`: updates an existing employee by email
   - `remove_employee`: removes an employee by email
   - `search_employees`: searches for employees by name, email, skills, or current role
   - `assign_shift`: schedules an employee for an 8-hour shift by name, date, and position

2. Call `list_employees` and verify the response contains the eight seeded employees as JSON, ordered by last name (Dubois first).

3. Call `assign_shift` with `employeeName: Kenji`, `date: 2026-08-01`, `position: sushi bar` and expect `Assigned Kenji Tanaka to 'sushi bar' on 2026-08-01 from 08:00 to 16:00.`

4. If all six tools are present and both calls return data, the server is healthy.
