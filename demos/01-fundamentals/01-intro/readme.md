# Get Started with Claude Code

Claude Code is Anthropic's agentic coding tool: a command-line interface that puts a capable AI directly inside your terminal, your IDE, or your CI pipeline. Unlike a chat assistant that answers questions, Claude Code acts: it reads files, writes code, runs tests, and coordinates multi-step tasks autonomously. This course teaches you how to work with it effectively, from first run to production-grade agentic workflows.

## The Claude Team

Anthropic ships Claude through a family of products, each designed for a different context and level of autonomy. They all share the same underlying models (Opus, Sonnet, Haiku) and all connect to the same Anthropic API, but their interfaces and capabilities are tuned for different use cases.

### Claude.ai

Claude.ai is the web-based chat interface at claude.ai. It is the fastest way to have a conversation with Claude without installing anything: you log in with an email address and start chatting immediately. It covers everyday tasks: drafting, summarizing, explaining concepts, quick code questions, and image understanding.

### Claude Desktop

Claude Desktop is the native application for macOS and Windows. It offers the same conversational experience as the web app but adds desktop-class integrations: local file access, MCP server connections, and the ability to control other apps on your machine. Claude Desktop is where many developers first encounter Claude's tool-use capabilities outside the browser.

### Claude Code CLI

Claude Code is the terminal-first tool and the central focus of this course. It is installed globally via npm (`npm install -g @anthropic-ai/claude-code`) and launched from any project directory with the `claude` command. Once running, it reads your codebase, understands the full project context, and can autonomously complete multi-file tasks (writing features, fixing bugs, running commands, and committing changes) without switching to a separate chat window.

```bash
# Start an interactive session in the current project
claude

# Run a one-shot task from the terminal
claude "Add input validation to the login form and write tests for it"
```

### Claude Code for VS Code and JetBrains

The Claude Code IDE extensions bring the same agentic capabilities into the editor. The [Claude Code extension for VS Code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) integrates the chat panel, inline diff reviews, and selection-aware context directly into the sidebar. JetBrains IDEs are supported through a separate plugin. Both extensions share session state with the CLI, so you can switch between terminal and IDE without losing context.

### Claude.ai/code

claude.ai/code is the browser-based entry point to Claude Code for users who prefer not to install the CLI. It provides a hosted coding environment where Claude can work on repositories and files directly in the browser. It targets developers who want agentic coding help without a local setup, and shares the same model and tool capabilities as the CLI.

### Claude for Work (Teams and Enterprise)

Claude for Work covers the Teams and Enterprise subscription tiers of Claude.ai. It adds collaboration features (shared projects, knowledge bases, and organization-level admin controls) on top of the standard chat experience. Enterprise deployments can connect to internal data sources and enforce data-handling policies required by regulated industries.

### Managed Agents and the Agent SDK

Managed Agents is Anthropic's platform for building and deploying production AI agents that run in the cloud. The Claude Agent SDK (available for Python and TypeScript) lets developers define custom agents, wire them to tools and data sources, and orchestrate multi-agent pipelines. This is the layer where Claude transitions from a developer tool into a software component inside a larger system.

### The Anthropic API

Everything in the Claude family is powered by the Anthropic API. Direct API access is for developers who want full control: choosing models, crafting system prompts, implementing tool use, and integrating Claude into their own products. The API supports streaming, prompt caching, batch processing, and the full range of Claude's multimodal capabilities.

## Why Claude Code for Developers

Claude Code occupies a unique position in the Claude family because it operates where code lives: in the terminal, in the IDE, and in CI/CD pipelines. It has persistent access to the full repository, can invoke shell commands, and understands git history. That combination enables workflows that a chat interface cannot match: autonomous multi-file refactors, test-driven bug fixes, and end-to-end feature implementation driven by a single natural-language prompt.

## Key Topics covered in this module

- [Claude Code documentation](https://code.claude.com/docs/en/overview)
- [Claude.ai](https://claude.ai)
- [Claude.ai/code](https://claude.ai/code)
- [Claude Desktop download](https://claude.ai/download)
- [Claude Code VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)
- [Anthropic API documentation](https://platform.claude.com/docs/en/api/overview)
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
- [Anthropic model overview](https://platform.claude.com/docs/en/about-claude/models/overview)
