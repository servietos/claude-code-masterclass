---
presents: demo-cache-meter.md
budget: 5 min
beats: 4
---

# Present: Install a Prompt-Cache Meter Mod

A mod installed from a gallery is reviewed before it runs, draws from the token counts every request reports, and takes its options only under its full plugin id. Four beats: the inventory, the band, the miss, the options file.

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
  ❯ ./prompt-cache-control.tsx calls: $.clock.every, $.command.register, $.env.get, $.fs.read (via readSetting), $.session.cwd (via readSetting), $.session.usage, $.ui.close, $.ui.invalidate, $.ui.log, $.ui.open, $.ui.resolve, $.ui.status, $.ui.toast
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

**Open:** [Step 5: Break the Cache on Purpose](demo-cache-meter.md#step-5-break-the-cache-on-purpose) · [Cache Lifetime](../../01-fundamentals/04-model-selection/readme.md#cache-lifetime)
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

### Beat 4: options live under the full plugin id, outside project settings (1 min)

**Open:** [`plugin.json`](cache-meter-solution/.claude/skills/prompt-cache-control/.claude-plugin/plugin.json) · the `userConfig` block
**Say:** A mod reads options from user settings, managed settings or a `--settings` file, never from project settings. The key is the id the plugin loaded under.

```json
    "prompt-cache-control@skills-dir": {
      "options": {
        "ttl": "1h",
        "warnSeconds": 120,
        "compactAtTokens": 50000,
        "status": true
```

**Result:** [`cache-meter.settings.json`](cache-meter-solution/cache-meter.settings.json), and `claude -p "/cache" --settings cache-meter.settings.json` naming the option as the lifetime source

```text
prompt-cache-control: 1h cache (the ttl option) · no request yet: the first one writes the cache · /cache stop closes
```

**Gotcha:** the installer's hint prints the key without `@skills-dir`, and an option under that key is silently ignored.

## If the room asks

| Question | Answer |
|---|---|
| Why does it load from `.claude/skills/` when it is not a skill? | Claude Code loads a plugin folder found there as `<name>@skills-dir` after the workspace trust prompt; `claude plugin list` shows it with project scope. |
| Can I try a mod without installing it? | Yes, `claude --plugin-dir <folder>` loads it for one session and hot-reloads it when a file changes. |
| Does `/cache` cost a model call? | No, `command.run` answers it inside the mod, so `claude -p "/cache"` returns at once; in Git Bash prefix `MSYS_NO_PATHCONV=1` or the shell rewrites `/cache` into a path. |
| Why one hour and not five minutes? | On a Claude subscription Claude Code asks for the one-hour lifetime; an API key or cloud provider gets five minutes unless `ENABLE_PROMPT_CACHING_1H=1` is set. |

## Runs live instead

A learner installs the mod into the pristine `cache-meter/` starter, causes the miss themselves and writes the settings file: [Install a Prompt-Cache Meter Mod](demo-cache-meter.md).
