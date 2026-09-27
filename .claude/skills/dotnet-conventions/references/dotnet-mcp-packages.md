# MCP NuGet packages and picking a version

## NuGet Packages

Core MCP packages:

```xml
<PackageReference Include="ModelContextProtocol" Version="2.2.0" />
<PackageReference Include="ModelContextProtocol.AspNetCore" Version="2.2.0" />
```

`dotnet package search ModelContextProtocol --exact-match` is not a reliable way to
pick a version. It has been observed returning only the oldest `0.1.0-preview.*`
entries; on 2026-08-28 it returned `1.0.0` through `2.2.0` ascending, with the current
version as the last row. Either way it is a truncated, ordering-dependent view and
`--take N` does not mean "the newest N". Read the flat index instead, which lists every
published version in order:

```bash
curl -s https://api.nuget.org/v3-flatcontainer/modelcontextprotocol/index.json
```

Confirm what actually resolved after `dotnet restore --force`, since a stale
`obj/project.assets.json` lets a build succeed against the old package:

```bash
grep -oE '"ModelContextProtocol(\.AspNetCore)?/[0-9][^"]*"' obj/project.assets.json | sort -u
```

**2.x is a silent behaviour change, not just a version bump.** The 1.x -> 2.0
breaking-change list touches nothing in the shape below (attributes, registration and
`Task<string>` tools all compile unchanged), so the upgrade looks free — but
`HttpServerTransportOptions.Stateless` now defaults to **true**. A single POST to
`/mcp` now answers `tools/list` with no session, and any curl recipe or doc that walks
`initialize` -> `Mcp-Session-Id` -> `notifications/initialized` is stale. Verify by
calling `tools/list` directly and counting the tools.

Back to the index: [dotnet-mcp](dotnet-mcp.md)
