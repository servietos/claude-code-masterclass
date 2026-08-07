# Install and Configure Claude Code

This module walks through installing Claude Code and all prerequisites on macOS and Windows, configuring the VS Code integration, and verifying the environment is ready for the rest of the course.

## Requirements

Claude Code runs as a Node.js CLI tool, so Node.js 18 or later is the only hard dependency. On macOS, the recommended path is Homebrew followed by `nvm` or the official Node.js installer. On Windows, download the LTS installer from nodejs.org or use `winget install OpenJS.NodeJS.LTS`.

Verify your Node.js installation before proceeding:

```bash
node --version   # must be 18 or later
npm --version
```

## Installing Claude Code

Claude Code is published to npm as `@anthropic-ai/claude-code`. Install it globally so the `claude` binary is available system-wide.

### macOS

```bash
npm install -g @anthropic-ai/claude-code
```

### Windows

Open a terminal (PowerShell or Command Prompt) as a regular user (not Administrator) and run:

```powershell
npm install -g @anthropic-ai/claude-code
```

## First-time Authentication

Run `claude` in any terminal to launch the interactive setup wizard. You will be prompted to authenticate either via a browser-based login (Anthropic Console) or by pasting an API key generated at console.anthropic.com.

```bash
claude
```

After authentication, Claude Code stores a session token locally and will not prompt again. Run `claude --version` to confirm the installation is working correctly.

## VS Code Extensions

Two extensions are recommended for working with Claude Code inside VS Code.

The [Claude Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) (publisher: `anthropic`) is the official Anthropic integration. It embeds Claude Code's chat and agent interface directly in the VS Code sidebar, adds editor-aware context such as the active file and selection, and surfaces inline diff views when Claude edits code. Install it from the Extensions panel by searching for "Claude Code" or via the marketplace link above.

The [Claude Terminal extension](https://marketplace.visualstudio.com/items?itemName=cjnoname.claude-terminal) (publisher: `cjnoname`) adds a dedicated terminal profile that launches Claude Code's interactive CLI pre-configured for the current workspace. It removes the need to open a separate terminal window and ensures the working directory is always set to the repo root.

Install both extensions from the command palette:

```text
ext install anthropic.claude-code
ext install cjnoname.claude-terminal
```

## Verifying the Environment

With Node.js, Claude Code, and the VS Code extensions installed, open a terminal in the root of any project and run:

```bash
claude --version
claude "What files are in this directory?"
```

A successful response confirms authentication and tool access are working. From here, proceed to the [CLAUDE.md Constitution](../04-constitution/readme.md) module.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/status` | Verify authentication is working and display current API key and model |
| `/help` | Show available slash commands and their descriptions |

## Key Topics covered in this module

- [Claude Code documentation](https://code.claude.com/docs/en/overview)
- [Node.js LTS download](https://nodejs.org/en/download)
- [Anthropic Console: API keys](https://console.anthropic.com/)
- [Claude Code VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)
- [Claude Terminal VS Code extension](https://marketplace.visualstudio.com/items?itemName=cjnoname.claude-terminal)
