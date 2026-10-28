# Dev Container for Agentic Software Engineering with Claude Code

## Purpose

This dev container provides a consistent, ready-to-use environment for the **Agentic Software Engineering with Claude Code** masterclass. It covers every runtime that the runnable projects under `demos/`, `labs/` and `src/` actually need, so a learner can clone the repo and start any module without local installs. Claude Code itself is installed globally, so `claude` is available in every terminal.

## What the Course Code Needs

The table maps each runtime to the code in the repository that requires it, including the projects nested in module subfolders.

| Runtime or tool                  | Provided by                | Used by                                                                                                                                                                                                                                  |
| -------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| .NET 10 SDK                      | base image                 | `demos/01-fundamentals/02-model-selection/model-routing-api`, `demos/04-mcp/02-mcp/hr-mcp-server`, `demos/04-mcp/03-mcp-apps/qr-mcp-app-cs`, `demos/05-subagents-agent-teams/**/catalog-service-cs*`, `src/food-app/catalog-api/catalog-service-cs*` |
| Node.js 22                       | `node` feature             | `demos/02-harness`, `demos/06-automate-cli`, `demos/07-optimize-observability`, `demos/10-sdk-managed-agents`, `labs/04-mcp/03-mcp-app`, `labs/06-automate-cli`, `labs/09-agentic-devops/react-devops`, `src/food-app/shop-ui`                                                   |
| Angular 21 CLI                   | via project `package.json` | `labs/04-mcp/01-using/food-shop-ng`, `src/food-app/shop-ui/food-shop-ng`                                                                                                                                                                 |
| Python 3.12                      | `python` feature           | `demos/04-mcp/01-intro/maf-migration`, `demos/11-planning/**/notes-cli`, `demos/10-sdk-managed-agents/**`, `labs/11-planning`, `src/qr-mcp-app-py`, `src/uuid-mcp-app-py-solution`                                                         |
| uv                               | post-create                | Python MCP servers started with `uv run server.py`, see `labs/03-skills` and `labs/04-mcp`                                                                                                                                               |
| Java 21 and Maven                | `java` feature             | `src/food-app/catalog-api/catalog-service-java`                                                                                                                                                                                          |
| Docker (docker-in-docker)        | `docker-in-docker` feature | `demos/04-mcp/02-mcp/hr-mcp-server/Dockerfile`, `demos/04-mcp/03-mcp-apps/qr-mcp-app-cs/Dockerfile`                                                                                                                                      |
| Azure CLI, azd, Bicep, Terraform | features plus post-create  | `demos/09-agentic-devops` (Azure deployment, IaC, Web Vitals)                                                                                                                                                                            |
| GitHub CLI                       | `github-cli` feature       | `demos/06-automate-cli`, `demos/09-agentic-devops`, PR and workflow demos                                                                                                                                                                         |
| Hugo Extended 0.128.0            | post-create                | `labs/09-agentic-devops/publish-blog` (design reference only; the module's Hugo lab builds the site inside a Docker container)                                                                                                           |
| Chrome for MCP browsing          | post-create                | `chrome-devtools` and `playwright` MCP servers in `/.mcp.json`                                                                                                                                                                           |
| PowerShell                       | `powershell` feature       | scripting demos and Windows-parity commands                                                                                                                                                                                              |
| Claude Code CLI                  | post-create                | every module                                                                                                                                                                                                                             |

## What's Inside

### Base Image

`mcr.microsoft.com/devcontainers/dotnet:10.0` gives the .NET 10 SDK plus the standard devcontainer tooling (git, curl, zsh).

### Dev Container Features

| Feature                                             | Version                   | Purpose                                     |
| --------------------------------------------------- | ------------------------- | ------------------------------------------- |
| `ghcr.io/devcontainers/features/node:2.0.0`         | 22.14.0                   | Angular, Vite, TypeScript, Claude Agent SDK |
| `ghcr.io/devcontainers/features/python:1`           | 3.12                      | Python MCP servers and Managed Agents demos |
| `ghcr.io/devcontainers/features/java:1`             | 21 (Microsoft JDK, Maven) | Spring Boot catalog service                 |
| `ghcr.io/devcontainers/features/azure-cli:1`        | latest                    | Azure resource management                   |
| `ghcr.io/azure/azure-dev/azd:latest`                | latest                    | Azure Developer CLI                         |
| `ghcr.io/devcontainers/features/terraform:1`        | latest                    | Infrastructure as Code module               |
| `ghcr.io/devcontainers/features/docker-in-docker:2` | latest                    | Building and running the MCP server images  |
| `ghcr.io/devcontainers/features/powershell:2.0.2`   | latest                    | PowerShell scripting                        |
| `ghcr.io/devcontainers/features/github-cli:1`       | latest                    | GitHub operations                           |

### Post-Create

Runs once after the container is first created:

- **Claude Code CLI** (`@anthropic-ai/claude-code`), the tool the whole class is about
- **uv**, the Python package runner used by the FastMCP servers
- **Hugo Extended 0.128.0**, required by the agentic DevOps lab
- **Bicep CLI** via `az bicep install`
- **Chrome**, so the `chrome-devtools` and `playwright` MCP servers can drive a browser
- Cleans stale `bin/` and `obj/` folders under `demos/`, `labs/` and `src/`, skipping `node_modules` and `.venv`

### Authentication and State

`ANTHROPIC_API_KEY` is passed through from the host environment when set, which the `demos/10-sdk-managed-agents` projects read. A named volume is mounted at `/home/vscode/.claude`, so a Claude Code login survives container rebuilds.

### Forwarded Ports

| Port  | Use                                        |
| ----- | ------------------------------------------ |
| 1313  | Hugo dev server                            |
| 3000  | Node demo servers                          |
| 3002  | QR MCP server registered in `/.mcp.json`   |
| 3003  | Map MCP server in `labs/04-mcp/03-mcp-app` |
| 4173  | Vite preview                               |
| 4200  | Angular dev server                         |
| 5000  | ASP.NET Kestrel HTTP                       |
| 5001  | ASP.NET Kestrel HTTPS                      |
| 5173  | Vite dev server                            |
| 6274  | MCP Inspector                              |
| 8000  | Python MCP over uvicorn                    |
| 47002 | HR MCP server in `demos/04-mcp`            |

## VS Code Extensions

### .NET and C#

- `ms-dotnettools.csharp`, `csdevkit`, `vscode-dotnet-runtime`, `vscodeintellicode-csharp`
- `aliasadidev.nugetpackagemanagergui`

### Web, Angular and TypeScript

- `angular.ng-template`
- `esbenp.prettier-vscode`

### Azure and Cloud

- `ms-azuretools.vscode-azurefunctions`, `vscode-azurecontainerapps`, `vscode-bicep`, `vscode-docker`
- `hashicorp.terraform`
- `ms-vscode.azurecli`

### AI and Claude

- `anthropic.claude-code`, the Claude Code integration
- `cjnoname.claude-terminal`
- `teamsdevapp.vscode-ai-foundry`
- `github.copilot`, `github.copilot-chat`
- `digitarald.agent-memory`

### Python

- `ms-python.python`, `vscode-pylance`, `vscode-python-envs`, `debugpy`

### Java

- `vscjava.vscode-java-pack` and the Spring Boot extensions

### Testing, Tooling and Authoring

- `ms-playwright.playwright`, `docker.docker`, `humao.rest-client`
- `github.vscode-pull-request-github`
- `mdickin.markdown-shortcuts`, `streetsidesoftware.code-spell-checker`, `kevinrose.vsc-python-indent`
- `vstirbu.vscode-mermaid-preview`, `bierner.markdown-mermaid`

## Quick Start (Local VS Code)

**Prerequisites**: Docker Desktop running, VS Code with the Dev Containers extension.

1. Clone the repo and open the folder in VS Code.
2. When prompted choose **Reopen in Container**, or use the Command Palette then `Dev Containers: Reopen in Container`.
3. Wait for the image build and post-create script to finish, roughly 5 to 10 minutes on first run.
4. Verify the toolchain:

```bash
claude --version
dotnet --version
node -v
python3 --version
uv --version
java --version
mvn --version
hugo version
terraform version
az --version | head -1
azd version
docker --version
```

### Rebuilding

Use **Dev Containers: Rebuild Container** after changing `Dockerfile`, `devcontainer.json`, or `post-create.sh`.

## Quick Start (GitHub Codespaces)

1. Navigate to the repository on GitHub.
2. Click **Code** then **Create codespace on master**.
3. Build and provisioning run automatically using the same `devcontainer.json`.

## Working With the Course Projects

Runnable project folders are starters and stay pristine, with no `node_modules`, no lockfile and no build output. The finished counterpart sits beside each one as `<starter>-solution/`. Installs and runs happen in the solution folder, so restore dependencies per project rather than repo-wide.

### Node and Angular projects

```bash
cd demos/10-sdk-managed-agents/01-api-surface/sdk-basics-solution
npm install
npm start
```

### .NET projects

```bash
cd demos/04-mcp/02-mcp/hr-mcp-server-solution
dotnet run
```

### Python MCP servers

```bash
cd src/qr-mcp-app-py-solution
uv run server.py --stdio
uv run server.py
```

### Java catalog service

```bash
cd src/food-app/catalog-api/catalog-service-java
mvn spring-boot:run
```

### Inspecting MCP tools

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json
```
