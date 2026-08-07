# Agent 365 CLI Quick Reference

## Install & Update

```powershell
# Install (preview — always use --prerelease)
dotnet tool install --global Microsoft.Agents.A365.DevTools.Cli --prerelease

# Update
dotnet tool update --global Microsoft.Agents.A365.DevTools.Cli --prerelease

# Verify
a365 -h
```

## Commands

```powershell
# Initialize configuration (requires custom client app registration)
a365 config init

# Publish agent
a365 publish

# Deploy to Azure Web App (optional)
a365 deploy
```

## Prerequisites

- .NET 8.0+
- Custom client app registration in Microsoft Entra ID with appropriate permissions (Global Administrator, Agent ID Administrator, or Agent ID Developer)
