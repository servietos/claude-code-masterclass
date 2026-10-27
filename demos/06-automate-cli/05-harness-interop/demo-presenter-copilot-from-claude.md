---
presents: demo-copilot-from-claude.md
budget: 7 min
beats: 4
---

# Present: Run Copilot CLI on DeepSeek From Claude Code

Two agent harnesses share one contract, so one can run the other as a shell command. Four beats: Copilot on DeepSeek with proof of the model, Claude calling Copilot interactively, `claude -p` chained into `copilot -p`, and Kimi K3 reviewing a plan Claude wrote.

------

**Setup:** no starter and no solution folder. The five `COPILOT_PROVIDER_*` and `COPILOT_MODEL` variables from [step 1](demo-copilot-from-claude.md#step-1-point-copilot-cli-at-deepseek-v41-flash) are set in the shell before the room arrives; the demo creates no files.

## Beats

### Beat 1: Copilot answers on your own model, and the event stream proves it (2 min)

**Open:** [`readme.md`](readme.md#bring-your-own-model-to-copilot-cli)
**Say:** Copilot CLI runs on GitHub's models until five variables point it at another provider. Here that is DeepSeek V4.1 Flash on a DeepInfra key.

```bash
copilot -p "create a poem about sighthounds" -s
copilot -p "create a poem about sighthounds" --output-format json | grep -E '"type":"(model.call_final_result|result)"'
```

**Result:** a poem, then two JSON lines

```json
{"type":"model.call_final_result","data":{"model":"deepseek-ai/DeepSeek-V4.1-Flash","isByok":true,"result":"success"},...}
{"type":"result","exitCode":0,"usage":{"premiumRequests":0,...}}
```

**Gotcha:** a `model` key in `~/.copilot/settings.json` beats `COPILOT_MODEL`. A hosted model name in this line means that file is winning.

### Beat 2: Claude calls Copilot like any other program (1 min)

**Open:** [`readme.md`](readme.md#calling-copilot-from-claude) · a `claude` session in the same shell
**Say:** Claude reaches Copilot through its Bash tool, the way it runs `git`. The provider variables travel with the child process.

```text
Run copilot -p 'create a poem about sighthounds' -s and show me the poem it returns.
```

**Result:** a Bash permission prompt for `copilot -p ...`, then Copilot's poem in Claude's reply

**Gotcha:** settings that already allow `Bash(copilot *)` skip the prompt; say so before the room wonders where it went.

### Beat 3: `claude -p` hands off to `copilot -p` with nobody watching (2 min)

**Open:** [`demo-copilot-from-claude.md`](demo-copilot-from-claude.md#step-4-chain-claude--p-into-copilot--p)
**Say:** Headless means nobody answers a prompt, so the permission goes on the command line.

```bash
claude -p "Run this shell command and return its stdout verbatim, nothing else: copilot -p 'create a poem about sighthounds' -s" --allowed-tools "Bash(copilot *)" --output-format json
```

**Result:** an envelope with `"is_error": false`, `"num_turns": 2`, `"permission_denials": []` and the poem in `result`

**Gotcha:** `total_cost_usd` (0.58 in the recorded run) is Claude's share only. The DeepSeek tokens bill to DeepInfra.

### Beat 4: Kimi K3 reviews a plan Claude wrote (2 min)

**Open:** a shell with the BYOK setup, where only the two model variables switch to [Kimi K3](https://deepinfra.com/moonshotai/Kimi-K3)
**Say:** Claude writes the plan and Copilot CLI on Kimi K3 gives a second opinion. Provider, base URL and key stay.

```bash
export COPILOT_MODEL=moonshotai/Kimi-K3
export COPILOT_PROVIDER_WIRE_MODEL=moonshotai/Kimi-K3
```

```powershell
$env:COPILOT_MODEL = "moonshotai/Kimi-K3"
$env:COPILOT_PROVIDER_WIRE_MODEL = "moonshotai/Kimi-K3"
```

Start `claude` in that shell and paste:

```text
Write a five-step plan, one line per step, for adding a /health endpoint to a small Express API. Then hand the plan to Kimi K3 for review: run copilot -p with the instruction 'Review this plan as a senior engineer. Name the two biggest risks and one missing step, in under 120 words.' followed by the plan, and the -s flag. Show me the plan, then Kimi's review verbatim.
```

**Result:** Claude's plan, then two risks and one missing step from Kimi

```text
1. Add a GET /health route that returns 200 with JSON { status: "ok", uptime, timestamp }.
2. Register the route before the auth and rate-limiting middleware so probes are never blocked.
3. Add a dependency check that pings the database and returns 503 when it is unreachable.
4. Write supertest tests covering the 200 and the 503 response.
5. Point the load balancer or container health check at /health and deploy.
```

```text
Risks

1. Liveness/readiness conflation: Returning 503 when the DB is down tells the orchestrator the process is unhealthy, triggering mass restarts of healthy app instances during a DB blip ... Split into /live (process up) and /ready (dependencies OK); only readiness should fail on DB errors.

2. Unauthenticated DB ping: Placing the dependency check before auth/rate-limiting lets anyone hammer your database via the public endpoint (DoS amplifier) and leaks infra details (uptime, DB topology). Keep the deep check authenticated/internal, or cache the result.

Missing step

No timeout or caching on the DB ping. A hanging connection makes /health hang, failing checks fleet-wide. Add a short timeout (e.g., 500ms) and cache the result for a few seconds.
```

With `--output-format json` on the `copilot -p` call, `model.call_final_result` names `"model":"moonshotai/Kimi-K3"` with `"isByok":true`.

**Gotcha:** set the two variables before `claude` starts. A session started earlier passes the DeepSeek values to Copilot.

## If the room asks

| Question | Answer |
|---|---|
| Does `gh copilot` work the same way? | On a recent GitHub CLI it starts the same `copilot` binary from PATH; Copilot flags go after `--`. |
| Why no `--allow-all-tools` on the Copilot side? | A text-only prompt calls no Copilot tools. A prompt that edits files needs `--allow-tool` or `--allow-all-tools`. |
