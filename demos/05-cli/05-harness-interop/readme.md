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

## Use Cases

Both use cases run in the shell from the BYOK setup above, so the DeepInfra key is already in `COPILOT_PROVIDER_API_KEY`.

### Kimi K3 Reviews a Plan

Claude writes a plan and hands it to Copilot CLI running [Kimi K3](https://deepinfra.com/moonshotai/Kimi-K3) as a second opinion. Only the two model variables change; provider, base URL and key stay.

```bash
export COPILOT_MODEL=moonshotai/Kimi-K3
export COPILOT_PROVIDER_WIRE_MODEL=moonshotai/Kimi-K3
```

```powershell
$env:COPILOT_MODEL = "moonshotai/Kimi-K3"
$env:COPILOT_PROVIDER_WIRE_MODEL = "moonshotai/Kimi-K3"
```

Start `claude` in that shell and paste the prompt:

```text
Write a five-step plan, one line per step, for adding a /health endpoint to a small Express API. Then hand the plan to Kimi K3 for review: run copilot -p with the instruction 'Review this plan as a senior engineer. Name the two biggest risks and one missing step, in under 120 words.' followed by the plan, and the -s flag. Show me the plan, then Kimi's review verbatim.
```

Claude's plan, from the recorded run:

```text
1. Add a GET /health route that returns 200 with JSON { status: "ok", uptime, timestamp }.
2. Register the route before the auth and rate-limiting middleware so probes are never blocked.
3. Add a dependency check that pings the database and returns 503 when it is unreachable.
4. Write supertest tests covering the 200 and the 503 response.
5. Point the load balancer or container health check at /health and deploy.
```

Kimi K3's review, trimmed:

```text
Risks

1. Liveness/readiness conflation: Returning 503 when the DB is down tells the orchestrator the process is unhealthy, triggering mass restarts of healthy app instances during a DB blip ... Split into /live (process up) and /ready (dependencies OK); only readiness should fail on DB errors.

2. Unauthenticated DB ping: Placing the dependency check before auth/rate-limiting lets anyone hammer your database via the public endpoint (DoS amplifier) and leaks infra details (uptime, DB topology). Keep the deep check authenticated/internal, or cache the result.

Missing step

No timeout or caching on the DB ping. A hanging connection makes /health hang, failing checks fleet-wide. Add a short timeout (e.g., 500ms) and cache the result for a few seconds.
```

Expected result: the plan, then two risks and one missing step. With `--output-format json`, Copilot's `model.call_final_result` event names `"model":"moonshotai/Kimi-K3"` with `"isByok":true`.

### Nano Banana Pro Draws an Image

Claude does not produce photorealistic images: it writes text and code, SVG diagrams included, and hands a photo to an image model. DeepInfra serves Nano Banana Pro as `google/nano-banana-pro` on its OpenAI-compatible images endpoint, so the same key creates images. Claude makes the call itself with `curl`. In the same `claude` session, paste:

```text
Create an image with Nano Banana Pro on DeepInfra: a photo of a female brindle whippet in the autumn winery hills of Vienna. Call https://api.deepinfra.com/v1/openai/images/generations with curl, model google/nano-banana-pro, size 1440x1080, and the key in $COPILOT_PROVIDER_API_KEY. Decode the b64_json field into whippet.png and tell me its pixel size.
```

The `curl` call Claude ran:

```bash
curl -sS -o response.json https://api.deepinfra.com/v1/openai/images/generations \
  -H "Authorization: Bearer $COPILOT_PROVIDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"google/nano-banana-pro","prompt":"A photo of a female brindle whippet standing in the autumn winery hills of Vienna, golden and red vine leaves on the rows of grapevines, rolling vineyard hills, soft autumn light, natural photography","size":"1440x1080","n":1,"response_format":"b64_json"}'
```

![A brindle whippet in the autumn vineyards above Vienna](../pptx/images/06-03-whippet-vienna.jpg)

Expected result: `whippet.png` and `response.json` in the current folder. The recorded image is 1408 x 768 pixels: Nano Banana Pro returned its own aspect ratio and ignored the requested `1440x1080`.

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
