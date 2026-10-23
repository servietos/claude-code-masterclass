# Get Started with Claude Code

Claude Code is Anthropic's agentic coding tool: it puts a capable AI inside your terminal, your IDE, or your CI pipeline. It reads files, writes code, runs tests, and coordinates multi-step tasks on its own. This topic places it in the Claude product family, installs it, and helps you pick the editor you work in for the rest of the course.

## Introduction to Claude Code

### The Claude Family

Anthropic ships Claude through a family of products, each tuned for a different context and level of autonomy. They all share the same models (Fable, Opus, Sonnet, Haiku) and the same Anthropic API.

| Product | What it is for |
|---------|----------------|
| [Claude.ai](https://claude.ai) | The web chat: log in and start, nothing to install. Drafting, summarizing, explaining concepts, quick code questions and image understanding |
| [Claude Desktop](https://claude.com/download) | The native app for macOS, Windows and Linux (beta). Adds local file access, MCP server connections and control of other apps, and includes Claude Code |
| Claude Code CLI | The terminal-first tool and the focus of this course. Reads your codebase and completes multi-file tasks: features, bug fixes, commands and commits |
| Claude Code for VS Code and JetBrains | The same agent inside the editor, with a chat panel, inline diff reviews and the current selection as context |
| [claude.ai/code](https://claude.ai/code) | Claude Code in the browser: a hosted environment that works on your repositories with no local setup |
| Claude for Work | The Team and Enterprise plans: shared projects, knowledge bases and organization-level admin controls, plus the data-handling policies regulated industries need |
| [Managed Agents and the Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) | Production agents in the cloud. The SDK (Python and TypeScript) defines agents, wires them to tools and data sources, and orchestrates multi-agent pipelines |
| [Anthropic API](https://platform.claude.com/docs/en/api/overview) | Full control for your own products: model choice, system prompts and tool use, with streaming, prompt caching, batch processing and multimodal input. Every product above runs on it |

### Why Claude Code for Developers

Claude Code operates where code lives: in the terminal, in the IDE, and in CI/CD pipelines. It keeps the full repository in reach, invokes shell commands, and understands git history. That combination enables autonomous multi-file refactors, test-driven bug fixes, and end-to-end feature work driven by a single natural-language prompt.

Start an interactive session in the current project with `claude`, or hand it a one-shot task:

```bash
claude
claude "Add input validation to the login form and write tests for it"
```

## Setup & Installation

### Install Claude Code

The native installer is the recommended path on every platform, and it keeps Claude Code updated in the background. On macOS, Linux and WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

On Windows, in PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Package managers work too: `brew install --cask claude-code` on macOS and `winget install Anthropic.ClaudeCode` on Windows, both updated only when you upgrade them yourself. To install through npm with Node.js, follow the [appendix](#appendix-install-with-npm-optional).

### Sign In

Run `claude` in any terminal to start the first-time login in your browser. Claude Code needs a Pro, Max, Team, Enterprise or Claude Console account; the free Claude.ai plan does not include it. Enterprise setups can also sign in through Amazon Bedrock, Google Cloud's Agent Platform or Microsoft Foundry.

```bash
claude
```

The login is stored locally, so later sessions start without a prompt. Use `/login` inside a session to switch accounts.

### Install the VS Code Extensions

The [Claude Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) (publisher `anthropic`) is the official integration. It embeds Claude Code's chat and agent interface in the sidebar, adds editor-aware context such as the active file and selection, and shows inline diffs when Claude edits code.

The [Claude Terminal extension](https://marketplace.visualstudio.com/items?itemName=cjnoname.claude-terminal) (publisher `cjnoname`) comes from an independent publisher; its listing states it has no affiliation with Anthropic. It runs the Claude Code CLI inside the editor at the workspace folder, alerts you when Claude finishes or needs a permission, and adds a session list and usage stats. The setup lab uses its shortcut.

Install both from the command palette:

```text
ext install anthropic.claude-code
ext install cjnoname.claude-terminal
```

### Verify the Environment

`claude --version` prints a version number followed by `(Claude Code)`. `claude doctor` prints read-only diagnostics on the install and your settings files, with a suggested fix for every warning.

```bash
claude --version
claude doctor
```

Then open a terminal in the root of any project and ask a first question. A successful answer confirms that the login and tool access work.

```bash
claude "What files are in this directory?"
```

## Editors: Terminal, Desktop App, VS Code

Claude Code runs in several environments, each suited to a different working style. The right choice depends on how much context you want from your editor, how often you switch between coding and conversation, and whether you need a local setup at all.

### Terminal

The terminal is the native home of Claude Code. After the install, the `claude` command works in any project directory with no further configuration: open a shell, change into a repository, and start working.

The interface is minimal by design. It gives you the full agent loop without IDE overhead, which fits remote development, SSH sessions and scripted one-shot tasks. It is also where the CLI flags and pipe-based workflows are most accessible.

### VS Code

VS Code is the recommended starting environment for this course. It is free and cross-platform, and the extension puts the full agent interface in the sidebar. With the IDE open beside the agent, you see git diffs, file explorer changes, test output and inline code decorations as they happen.

Claude reads the active file and the current selection automatically, and shows each edit as an inline diff before it is applied. For developers new to agentic work, that makes the feedback loop easy to follow. The integrated terminal runs the CLI as well, so you can move between the sidebar and the command line without leaving the editor.

Cursor installs the same extension. JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm) use the [Claude Code plugin](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-), which drives the CLI, so install the CLI first.

### Desktop App

Claude Desktop is Anthropic's native app for macOS and Windows, with a Linux beta. It includes Claude Code, so you can run coding sessions without installing the CLI; this needs a paid plan.

The same app is also the conversation interface with desktop integration: local file access, MCP server connections, and control of other apps on your machine. It suits talking through architecture decisions, reviewing documents, or using MCP-connected tools outside a coding session.

### Claude Code on the Web

[claude.ai/code](https://claude.ai/code) runs Claude Code in the browser with no local setup. It fits a machine where you cannot install the CLI, or a quick task on a repository away from your own workstation.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/login` | Sign in to your Anthropic account, or switch to another one |
| `/status` | Open Settings on the Status tab: version, model, account and connectivity |
| `/doctor` | Run a setup checkup of the installation, settings, extensions and `CLAUDE.md`, then apply the proposed fixes after you confirm |
| `/help` | Show help and the commands available in this session |

## Key Topics covered in this module

- [Claude Code overview](https://code.claude.com/docs/en/overview)
- [Set up Claude Code](https://code.claude.com/docs/en/setup)
- [Quickstart](https://code.claude.com/docs/en/quickstart)
- [Claude Code in VS Code](https://code.claude.com/docs/en/vs-code)
- [Claude Code in JetBrains IDEs](https://code.claude.com/docs/en/jetbrains)
- [Claude Code Desktop](https://code.claude.com/docs/en/desktop)
- [Claude Code on the web](https://claude.ai/code)
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
- [Anthropic API](https://platform.claude.com/docs/en/api/overview)
- [Models overview](https://platform.claude.com/docs/en/models/overview)

## Appendix: Install with npm (Optional)

Claude Code is also published to npm as `@anthropic-ai/claude-code`. The package needs Node.js 22 or later; an older version prints an `EBADENGINE` warning and installs anyway, so check first.

On macOS, install Node.js with the LTS installer from [nodejs.org](https://nodejs.org/en/download), with Homebrew (`brew install node`), or with `nvm`. On Windows, use the LTS installer or `winget install OpenJS.NodeJS.LTS`, then open a new terminal.

```bash
node --version
npm --version
```

Install the package globally so the `claude` binary is available system-wide. On Windows, open PowerShell or Command Prompt as a regular user, without Administrator rights.

```bash
npm install -g @anthropic-ai/claude-code
```

Then continue with [Sign In](#sign-in).
