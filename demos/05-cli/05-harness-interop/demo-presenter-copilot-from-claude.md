---
presents: demo-copilot-from-claude.md
budget: 5 min
beats: 3
---

# Present: Run Copilot CLI on DeepSeek From Claude Code

Two agent harnesses share one contract, so one can run the other as a shell command. Three beats: Copilot on DeepSeek with proof of the model, Claude calling Copilot interactively, and `claude -p` chained into `copilot -p`.

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

## If the room asks

| Question | Answer |
|---|---|
| Does `gh copilot` work the same way? | On a recent GitHub CLI it starts the same `copilot` binary from PATH; Copilot flags go after `--`. |
| Why no `--allow-all-tools` on the Copilot side? | A text-only prompt calls no Copilot tools. A prompt that edits files needs `--allow-tool` or `--allow-all-tools`. |
