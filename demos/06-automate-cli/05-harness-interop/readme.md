# Harness Interop

> **_NOTE:_** Duration: about 15 minutes.

Claude Code and GitHub Copilot CLI share one contract: give either a prompt with `-p` and it works, prints to stdout and exits with a code. Each is a program in the terminal, so one harness can run the other as a shell command. Here Claude Code drives Copilot CLI, and Copilot runs on DeepSeek V4.1 Flash through your own DeepInfra key.

## Two Harnesses, One Contract

The flags carry different names and do the same jobs.

| Purpose | Claude Code | Copilot CLI |
|---|---|---|
| Run one prompt and exit | `claude -p "..."` | `copilot -p "..."` |
| Print only the answer | default text output | `-s` drops the usage stats footer |
| Machine-readable output | `--output-format json`: one envelope | `--output-format json`: JSONL, one event per line |
| Pre-approve tools | `--allowed-tools` | `--allow-tool` or `--allow-all-tools` |
| Deny tools | `--disallowed-tools` | `--deny-tool` |

## Bring Your Own Model to Copilot CLI

Five environment variables move Copilot CLI off GitHub's hosted models; `copilot help providers` lists them.

| Variable | Value for DeepSeek V4.1 Flash on DeepInfra |
|---|---|
| `COPILOT_PROVIDER_TYPE` | `openai` |
| `COPILOT_PROVIDER_BASE_URL` | `https://api.deepinfra.com/v1/openai` |
| `COPILOT_PROVIDER_API_KEY` | your DeepInfra key |
| `COPILOT_MODEL` | `deepseek-ai/DeepSeek-V4.1-Flash` |
| `COPILOT_PROVIDER_WIRE_MODEL` | `deepseek-ai/DeepSeek-V4.1-Flash` |

A `model` key in `~/.copilot/settings.json` beats `COPILOT_MODEL`, so check that file when a run ignores your variables. The proof of which model answered is in the event stream: `model.call_final_result` names the model with `"isByok": true`, and the closing `result` event reports `"premiumRequests": 0`.

## Calling Copilot From Claude

Claude reaches Copilot through its Bash tool, and the child process inherits the shell's environment, so the provider variables flow from `claude` into `copilot` untouched. In an interactive session you approve the call at the permission prompt. In a headless chain, `--allowed-tools "Bash(copilot *)"` on the `claude -p` command line approves it up front.

Each harness guards its own side. Claude's rule decides whether `copilot` starts; Copilot's `--allow-tool` and `--deny-tool` decide what it may do once running. Claude's `total_cost_usd` counts Claude's tokens only, because DeepInfra bills the DeepSeek tokens to your key.

On a recent GitHub CLI, `gh copilot` starts the same `copilot` binary from your PATH and forwards flags placed after `--`.

## Hands-On Demo

[Run Copilot CLI on DeepSeek From Claude Code](demo-copilot-from-claude.md) sends one prompt, `create a poem about sighthounds`, through Copilot alone, through Claude interactively and through `claude -p`.

## Helpful Claude Code CLI Commands

| Command | Usage |
|---|---|
| `claude -p "..." --allowed-tools "Bash(copilot *)" --output-format json` | Let a headless Claude run hand work to Copilot CLI without a prompt. |
| `copilot -p "..." -s` | Run Copilot CLI headless and print only its answer. |
| `copilot -p "..." --output-format json` | Stream Copilot's events as JSONL to read the model and premium-request count. |

## Key Topics Covered in This Module

- [Claude CLI reference](https://code.claude.com/docs/en/cli-reference): `-p`, `--allowed-tools`, `--output-format`
- [Claude headless mode](https://code.claude.com/docs/en/headless): the JSON envelope
- [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli): non-interactive use and your own model provider
- [gh copilot](https://cli.github.com/manual/gh_copilot): the GitHub CLI command that starts Copilot CLI
- [DeepSeek V4.1 Flash on DeepInfra](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash): model page and pricing
- [Kimi K3 on DeepInfra](https://deepinfra.com/moonshotai/Kimi-K3): model page and pricing

## Appendix

- [Configure DeepSeek V4.1 Flash and Kimi K3 in VS Code Copilot Chat](appendix-oai-compatible-copilot.md): the OAI Compatible Provider for Copilot extension
