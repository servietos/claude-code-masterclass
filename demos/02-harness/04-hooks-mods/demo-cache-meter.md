# Install a Prompt-Cache Meter Mod

Today you find out what a session cost only after the fact, and a cache miss that doubled the bill leaves no trace on screen. You install a community mod that draws a live cache meter above the prompt, check what it can reach before you trust it, and watch it name a miss you cause on purpose.

------

Work in `cache-meter/`, a small TypeScript sample with a `CLAUDE.md`; the finished result is beside it in `cache-meter-solution/`.

## Step 1: Read What the Mod Can Reach Before You Trust It

**Overview:** A mod is a plugin, and the `claude-code-templates` gallery copies its files straight into the project, where it runs with your permissions and is not sandboxed. `claude plugin validate` reads the hooks module without running it and lists every event it handles, every mods API method it calls and every environment variable it reads.

```bash
npx claude-code-templates@latest --mod observability/prompt-cache-control
```

```bash
claude plugin validate .claude/skills/prompt-cache-control
```

**Expected Outcome:** Six files land under `.claude/skills/prompt-cache-control/`, and the validation passes with the whole inventory of what the mod does:

```text
  ❯ ./prompt-cache-control.tsx hooks: session.start, session.end, turn.step, command.run{command=cache}, ui.close, ui.press, ui.render{component=AbovePrompt}, ui.render{component=Pane}
  ❯ ./prompt-cache-control.tsx gating hook without .catch: command.run{command=cache}
  ❯ ./prompt-cache-control.tsx gating hook without .catch: ui.close
  ❯ ./prompt-cache-control.tsx calls: $.clock.every, $.command.register, $.env.get, $.fs.read (via readSetting), $.session.cwd (via readSetting), $.session.usage, $.ui.close, $.ui.invalidate, $.ui.log, $.ui.open, $.ui.resolve, $.ui.status, $.ui.toast
  ❯ ./prompt-cache-control.tsx env writes: nothing
  ❯ ./prompt-cache-control.tsx env reads: CLAUDE_CODE_PROMPT_CACHE_TTL, DISABLE_PROMPT_CACHING, DISABLE_PROMPT_CACHING_HAIKU, DISABLE_PROMPT_CACHING_OPUS, DISABLE_PROMPT_CACHING_SONNET, ENABLE_PROMPT_CACHING_1H, FORCE_PROMPT_CACHING_5M, HOME

✔ Validation passed
```

Read it as a reviewer: no `tool.call` hook, so it cannot hold or rewrite anything Claude runs, and no network call. Ignore the installer's early-access warning about `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`: mods are on by default from Claude Code 2.1.287.

## Step 2: Break the Cache on Purpose

**Overview:** The band above the prompt is drawn by the mod's `ui.render` hook on `AbovePrompt`, from the token counts every request reports. Every model has its own cache, so a model switch makes the next request write the whole history again.

Start a session with `claude`, accept the workspace trust prompt so Claude Code loads the mod from `.claude/skills/`, and send these two prompts one after the other:

```text
Read src/types.ts and list the members of the ErrorCode union, one line each.
```

```text
Now read src/orders.ts and name the exported functions.
```

After each turn the band shows the hit rate, the tokens read from the cache, and a countdown to expiry:

```text
● cache ██████████ 99% read 84.8k ⏱ 59:18 1h · warm: keep going
                        wrote 369
                        new 2
```

Switch the model with `/model haiku`, confirm the dialog, send one more prompt, then open the pane with `/cache`:

```text
Read src/users.ts and name its exported functions.
```

**Expected Outcome:** Turn 3 wrote 64.5k tokens to a fresh cache in its first request, so its hit rate drops to 50% while turn 2 sat at 100%:

```text
turn steps   read  wrote   new  hit
   1     2  84.8k  85.7k     4  50%
   2     2   172k    442     4 100%
   3     2  64.2k  64.5k    18  50%
```

`/model` also saved Haiku as your default for new sessions, so run `/model default` before you leave.
