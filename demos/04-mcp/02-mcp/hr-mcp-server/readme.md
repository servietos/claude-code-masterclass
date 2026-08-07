# hr-mcp-server (Demo Project)

This folder is the starter you work in. The completed reference lives beside it in `hr-mcp-server-solution/`.

## Prerequisites

- .NET SDK 10.0 or later (`dotnet --version`)
- Node.js, only for the MCP Inspector step

## Remote deployment (optional)

After you publish the server to your own App Service, put its hostname into the `hr-mcp-azure-dev` entry of `inspector.config.json` and select that entry:

```powershell
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp-azure-dev
```

The URL shipped in that entry points at an App Service that is no longer deployed, so replace it with your own hostname before running the command.

> **Heads-up:** Updating `inspector.config.json` is a local workflow change only: you do not need to republish the App Service after editing this file. Republish the .NET app itself only when the server code or the configuration inside the deployed artifact changes.
