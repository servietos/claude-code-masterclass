---
presents: demo-cache-meter.md
budget: 4 min
beats: 3
---

# Present: Install a Prompt-Cache Meter Mod

A mod installed from a gallery is reviewed before it runs and draws from the token counts every request reports. Three beats: the inventory, the band, the miss.

------

## Beats

### Beat 1: a mod is reviewed before it runs, from its own inventory (1 min)

**Open:** [`hooks/hooks.json`](cache-meter-solution/.claude/skills/prompt-cache-control/hooks/hooks.json) · the `modules` key that makes the plugin a mod
**Say:** A mod runs with your permissions and nothing sandboxes it. The validator reads the source without running it and prints everything it can touch.

```json
{
  "description": "prompt-cache-control: turn.step reads each request's cache usage; a one-second clock.every drives the countdown; ui.render draws the AbovePrompt band and the /cache pane",
  "modules": [
    "./prompt-cache-control.tsx"
  ]
}
```

**Result:** `claude plugin validate` on the installed copy, with no `tool.call` hook and no network call in the list

```text
  ❯ ./prompt-cache-control.tsx hooks: session.start, session.end, turn.step, command.run{command=cache}, ui.close, ui.press, ui.render{component=AbovePrompt}, ui.render{component=Pane}
  ❯ ./prompt-cache-control.tsx gating hook without .catch: command.run{command=cache}
  ❯ ./prompt-cache-control.tsx gating hook without .catch: ui.close
  ❯ ./prompt-cache-control.tsx calls: $.clock.every, $.command.register, $.env.get, $.fs.read (via readSetting), $.session.cwd (via readSetting), $.session.usage, $.ui.close, $.ui.invalidate, $.ui.log, $.ui.open, $.ui.resolve, $.ui.status, $.ui.toast
  ❯ ./prompt-cache-control.tsx env writes: nothing
  ❯ ./prompt-cache-control.tsx env reads: CLAUDE_CODE_PROMPT_CACHE_TTL, DISABLE_PROMPT_CACHING, DISABLE_PROMPT_CACHING_HAIKU, DISABLE_PROMPT_CACHING_OPUS, DISABLE_PROMPT_CACHING_SONNET, ENABLE_PROMPT_CACHING_1H, FORCE_PROMPT_CACHING_5M, HOME
✔ Validation passed
```

**Gotcha:** the installer's warning about `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` is stale; from 2.1.287 mods are on by default and the variable is ignored.

### Beat 2: the band is four token counts per request, observed and passed on (1.5 min)

**Open:** [`prompt-cache-control.tsx`](cache-meter-solution/.claude/skills/prompt-cache-control/hooks/prompt-cache-control.tsx) · the `turn.step` hook
**Say:** The hook lets the request run first, then reads the usage it reported. It never changes the request, which is the observe shape.

```tsx
  on('turn.step', async function* ($, e, next) {
    if (e.agentId) return yield* next(e)
    const startedAt = Date.now()
    const r = yield* next(e)
    if (r.usage) {
      samples.push({
        ...
        read: r.usage.cache_read_input_tokens,
        write: r.usage.cache_creation_input_tokens,
```

**Result:** the band after the second turn on a Claude subscription, with no file written

```text
● cache ██████████ 99% read 84.8k ⏱ 59:18 1h · warm: keep going
                        wrote 369
                        new 2
```

**Gotcha:** a high hit rate on the first turn is real, because the system prompt and tool definitions were cached by earlier sessions in the same directory.

### Beat 3: a model switch rewrites the whole history (1.5 min)

**Open:** [Step 2: Break the Cache on Purpose](demo-cache-meter.md#step-2-break-the-cache-on-purpose) · [Cache Lifetime](../../01-fundamentals/02-model-selection/readme.md#cache-lifetime)
**Say:** Every model has its own cache. Claude Code warns you before the switch, and the pane prices it per turn.

```text
   This conversation is cached for the current model. Switching to Haiku 4.5 means the full history gets re-read on your next message.
   ❯ 1. Yes, switch to Haiku 4.5
     2. No, go back
```

**Result:** the `/cache` pane, where turn 3 wrote 64.5k tokens to a fresh cache and its hit rate fell to 50%

```text
turn steps   read  wrote   new  hit
   1     2  84.8k  85.7k     4  50%
   2     2   172k    442     4 100%
   3     2  64.2k  64.5k    18  50%
```

**Gotcha:** `/model haiku` also saves Haiku as the default for every new session; `/model default` puts it back.

## If the room asks

| Question | Answer |
|---|---|
| Why does it load from `.claude/skills/` when it is not a skill? | Claude Code loads a plugin folder found there as `<name>@skills-dir` after the workspace trust prompt; `claude plugin list` shows it with project scope. |
| Can I try a mod without installing it? | Yes, `claude --plugin-dir <folder>` loads it for one session and hot-reloads it when a file changes. |
| Why one hour and not five minutes? | On a Claude subscription Claude Code asks for the one-hour lifetime; an API key or cloud provider gets five minutes unless `ENABLE_PROMPT_CACHING_1H=1` is set. |

## Runs live instead

A learner installs the mod into the pristine `cache-meter/` starter and causes the miss themselves: [Install a Prompt-Cache Meter Mod](demo-cache-meter.md).
