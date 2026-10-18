# Build a Custom MCP Server in C#

This demo contains a production-style MCP server built with C# .NET 10 and ASP.NET Core, serving as a practical reference for writing real-world MCP tools. The server exposes HR management capabilities over the Streamable HTTP transport, making it consumable by any MCP-compatible client, including Claude Desktop, GitHub Copilot, and the MCP Inspector.

Hands-on demo: [Build an HR MCP Server with Streamable HTTP](demo-hr-mcp-server.md).

## HR MCP Server

The [hr-mcp-server/](hr-mcp-server) project implements a restaurant HR management backend as a set of MCP tools. It uses `ModelContextProtocol` 1.2.0 and `ModelContextProtocol.AspNetCore` 1.2.0 to expose tools over Streamable HTTP on port 47002. Entity Framework Core 10 with a SQLite backend persists employee and shift data across server restarts.

The server registers six tools, each decorated with `[McpServerTool]` and `[Description]` attributes that Claude and other AI clients read as tool metadata:

- `list_employees`: retrieves all employees ordered by last name
- `add_employee`: creates a new employee with role, skills, and spoken languages
- `update_employee`: applies partial updates to an existing employee by email
- `remove_employee`: deletes an employee by email
- `search_employees`: searches across name, email, role, skills, and languages
- `assign_shift`: schedules an employee for an 8-hour shift on a given date and position

The [Tools/HRTools.cs](hr-mcp-server/Tools/HRTools.cs) class is annotated with `[McpServerToolType]`, which lets `WithToolsFromAssembly()` discover and register all tools automatically via ASP.NET Core's dependency injection. Skills and spoken languages on the [Tools/Models.cs](hr-mcp-server/Tools/Models.cs) `Employee` model are stored as JSON arrays in SQLite columns using a backing-field pattern with `[NotMapped]` projected properties.

On first launch, [Data/EmployeeDbInitializer.cs](hr-mcp-server/Data/EmployeeDbInitializer.cs) seeds eight restaurant staff members with multilingual profiles and role-specific skill sets. The [Program.cs](hr-mcp-server/Program.cs) wires up EF Core, the employee service, and the MCP server in a minimal ASP.NET Core host before calling `app.MapMcp()` to expose the MCP endpoint.

You work in the starter at [hr-mcp-server/](hr-mcp-server); the finished result lives beside it in `hr-mcp-server-solution/`.

![HR MCP server tools discovered by an MCP client](hr-mcp-server/mcp-integration.png)

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/mcp` | Confirm Claude Code picked up the `hr-mcp` entry and list the six HR tools it now sees |
| `/doctor` | Diagnose a failed connection to `http://localhost:47002` before blaming the server code |
| `/update-config` | Add or edit the `hr-mcp` entry in the project-level `.mcp.json` |

## Key Topics covered in this module

- [Model Context Protocol documentation](https://modelcontextprotocol.io/docs/getting-started/intro)
- [ModelContextProtocol NuGet package](https://www.nuget.org/packages/ModelContextProtocol)
- [ModelContextProtocol.AspNetCore NuGet package](https://www.nuget.org/packages/ModelContextProtocol.AspNetCore)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Entity Framework Core with SQLite](https://learn.microsoft.com/en-us/ef/core/providers/sqlite/)
