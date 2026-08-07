# Connect MCP Servers to the Harness

An MCP server is what turns "Claude can describe this" into "Claude can do this". With the playwright and github servers registered, both prompts below run against the live system instead of against the model's memory of it:

```text
Open http://localhost:4200 at 375px wide, screenshot it, and tell me what overflows.
```

```text
List the open pull requests on this repo and flag any that touch .github/workflows.
```

Neither needed integration code. The servers are declared in `.mcp.json`, their tools appear in the session, and each call still asks for your approval before it runs.

Model Context Protocol (MCP) is the open standard for securely connecting AI models to external data sources, tools, and services. Instead of embedding integrations directly into applications, MCP decouples the client from the server, allowing Claude and other AI systems to access capabilities through a standardized interface. This architecture lets you connect everything from REST APIs to databases, file systems, and specialized business logic, without rewriting your entire system.

An MCP server is a separate process that exposes tools, resources, and prompts to clients like Claude Code or Claude.ai. Servers communicate over three transport types: stdio for local processes, HTTP for remote endpoints, and WebSocket for bidirectional connections. Clients discover and invoke tools by querying the server's schema, and every tool call requires explicit approval, giving you full control over what Claude can do.

## Architecture Overview

MCP follows a client-server model where the client initiates connections, discovers available tools, and sends requests. Servers run independently and expose their capabilities through a standardized interface. This separation means you can swap implementations, update tools without changing the client, and scale servers across infrastructure without modifying Claude's configuration.

Transports determine how messages flow. Stdio works for local processes like the Angular CLI or playwright; the server starts as a subprocess and communicates through standard input/output. HTTP is for hosted endpoints that need to be accessible from anywhere. WebSocket enables real-time bidirectional communication. You configure which transport to use in your `.mcp.json` file.

## Available MCP Servers

The `.mcp.json` configuration file in your workspace registers eight MCP servers that extend Claude Code's capabilities:

| Server | Type | Purpose |
|--------|------|---------|
| qr-code | HTTP (localhost:3002) | Generate QR code PNG images from text or URLs |
| ssh-mcp | stdio | Hold an SSH connection to the Ubuntu host configured in `.mcp.json`, run commands with sudo, and return structured results |
| context7 | HTTP | Retrieve documentation and code examples from programming libraries and frameworks |
| playwright | stdio | Browser automation for testing, scraping, and visual interactions |
| angular-cli | stdio | Analyze, refactor, and run Angular projects with version-specific best practices |
| azure-deploy | stdio | Azure resource management, deployment planning, and IaC generation (Bicep/Terraform) |
| github | HTTP | Repository management, pull requests, issues, and code review automation |
| microsoft-learn | HTTP | Search and fetch official Microsoft documentation and code samples |

Each server can be enabled or disabled in Claude Code. When enabled, the available tools appear in your assistant's context, and every tool invocation requires your explicit approval before execution.

## Discovering MCP Servers

The MCP ecosystem includes several public registries for discovering pre-built servers:

- **MCP.so**: One of the largest community-driven directories; searchable by category and use case. Hundreds of servers for databases, APIs, productivity tools, and custom integrations.
- **Anthropic's MCP GitHub Repository**: The official reference list of MCP servers maintained by Anthropic. Includes implementation examples, best practices, and community contributions. Start here for well-tested servers and architectural patterns.
- **Claude.ai MCP Connector Directory**: The curated list of what's actually available to connect within Claude.ai itself. Updated as Anthropic and partners release new integrations.
- **[GitHub MCP Registry](https://github.com/mcp)**: GitHub's own catalog of over 200 servers that connect models to files, APIs and databases. Each listing carries install options and download counts, so popularity is visible before you commit to a server.
- **[Smithery](https://smithery.ai)**: The largest hosted registry, with more than 13,900 servers. It hosts servers for you and handles OAuth, credentials and sessions, so `npx smithery mcp add <name>` is usually the whole setup.
- **[Official MCP Registry](https://registry.modelcontextprotocol.io)**: Maintained by the MCP contributors themselves. Searchable by name and version, and exposed as an API, which makes it the right source when you want to script discovery rather than browse it.

## Developer Use Cases

### Playwright for Test Automation

Playwright MCP lets you automate browser interactions without writing Selenium or Puppeteer code yourself. You describe what you want tested ("visit the login page, fill the form with test credentials, verify the dashboard loaded") and Claude handles the script generation and execution. This cuts testing setup time from hours to minutes and catches layout regressions before they reach production.

### Azure Deploy for Infrastructure Planning

Azure Deploy MCP translates your infrastructure requirements into production-ready Bicep templates, Terraform modules, or ARM deployments. Describe your application architecture ("Node.js API with Azure SQL, static web frontend, scheduled background jobs") and get cost estimates, security recommendations, and deployment pipelines. You avoid boilerplate, stay aligned with Azure best practices, and deploy with confidence.

### GitHub MCP for Code Review Automation

GitHub MCP streamlines PR workflows. Claude can list pending reviews, read PR diffs, comment on specific lines, and even suggest fixes. Instead of manually reviewing each PR in the interface, you can ask Claude to "review all open pull requests and flag security issues", and watch it add targeted comments. This lets your team focus on architecture decisions while routine reviews happen automatically.

### Microsoft Learn MCP for Project Analysis & Upgrade Guidance

The Microsoft Agent Framework (MAF) is a Python/TypeScript framework for building AI agents that run on Azure. MAF agents orchestrate tool calls, maintain state, and execute complex multi-step workflows using Claude or other supported models. Unlike simple chatbots, MAF agents can plan sequences of actions, recover from errors, and integrate deeply with Azure services, making them ideal for production automation, data pipelines, and business logic. This module covers how to wrap MAF agents and other services as MCP servers so Claude Code can invoke them directly, and how to keep your MAF implementations current as the framework evolves.

Microsoft Learn MCP connects you to official Microsoft documentation and code samples in real time. Instead of manual doc searches, you ask Claude directly and get answers grounded in current best practices. Try this workflow with the MAF starter solution in `demos/02-harness/04-mcp/maf-migration`:

```text
Read the project structure in demos/02-harness/04-mcp/maf-migration.
Search Microsoft Learn for the latest Microsoft Agent Framework patterns and best practices.
Compare my code against those standards and flag anything outdated or deprecated.
Show me the breaking changes between my current version and what's recommended.
Generate a migration plan with code examples.
```

Claude queries live documentation, analyzes your codebase, identifies gaps, and generates a step-by-step upgrade guide with examples. Since MAF is pre-release software, breaking changes happen frequently, and this prompt-driven approach keeps you synchronized with what's current so you can upgrade confidently and catch deprecations before they break your build.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/update-config` | Register, disable, or configure MCP servers in `.mcp.json` and `settings.json`. |
| `/doctor` | Diagnose MCP server connectivity issues and verify which servers are active. |
| `/find-skills` | Discover skills that wrap MCP servers with domain-specific instructions. |

## Key Topics Covered in This Module

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/): Official MCP specification and architecture
- [Anthropic MCP GitHub Repository](https://github.com/modelcontextprotocol): Reference implementations and community servers
- [MCP.so Registry](https://mcp.so): Searchable directory of community MCP servers
- [Claude Code Documentation](https://claude.com/product/claude-code): Using Claude Code with MCP servers
