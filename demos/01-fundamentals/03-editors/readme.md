# Choose Your Editor

Claude Code runs in three distinct environments, each suited to a different working style. The right choice depends on how much context you want from your editor, how often you switch between coding and conversation, and whether you need a local setup at all.

## Terminal

The terminal is the native home of Claude Code. After a global install, the `claude` command works in any project directory with no additional configuration: open a shell, navigate to a repo, and start working.

```bash
claude
```

The terminal interface is minimal by design. It gives you the full agent loop without any IDE overhead, which makes it a good fit for remote development, SSH sessions, and scripted one-shot tasks. It is also the environment where Claude Code's CLI flags and pipe-based workflows are most accessible.

## VS Code

VS Code is the recommended starting environment for this course. It is free, cross-platform, and the [Claude Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) integrates the full agent interface directly into the sidebar. Because the IDE remains open alongside the agent, you see git diffs, file explorer changes, test output, and inline code decorations in real time, context that a standalone terminal window does not surface.

The extension also adds editor-aware features: Claude reads the active file and current selection automatically, and edits are shown as inline diffs before they are applied. For developers new to agentic workflows, this makes the feedback loop tangible and easy to follow.

VS Code's integrated terminal runs Claude Code just as a standalone terminal would, so you can switch between the sidebar chat and the CLI without leaving the editor. Installing both the Claude Code extension and the [Claude Terminal extension](https://marketplace.visualstudio.com/items?itemName=cjnoname.claude-terminal) gives you the most complete setup.

```text
ext install anthropic.claude-code
ext install cjnoname.claude-terminal
```

## Claude Desktop App

Claude Desktop is the native macOS and Windows application from Anthropic. Unlike the terminal or VS Code extension, it is not a coding environment; it is a conversation interface with added desktop integration: local file access, MCP server connections, and the ability to interact with other apps on your machine.

Claude Desktop is useful when you want to talk through architecture decisions, review documents, or use MCP-connected tools outside of a coding session. It shares the same underlying models as the CLI and can connect to the same MCP servers configured in your project.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/model` | Switch between Claude models (Fable, Opus, Sonnet, Haiku) mid-session |
| `/status` | Display current editor environment and session info |
| `/help` | List all available slash commands in the current environment |

## Key Topics covered in this module

- [Claude Code extension for VS Code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)
- [Claude Terminal extension for VS Code](https://marketplace.visualstudio.com/items?itemName=cjnoname.claude-terminal)
- [Claude Desktop download](https://claude.ai/download)
- [Claude Code documentation](https://code.claude.com/docs/en/overview)
