# Install a Prompt-Cache Meter Mod

Today you find out what a session cost only after the fact, and a cache miss that doubled the bill leaves no trace on screen. You install a community mod that draws a live cache meter above the prompt, check what it can reach before you trust it, watch it name a miss you cause on purpose, and pin its options in a settings file. You finish with a project that shows its own cache health on every turn.

------

Work in `cache-meter/`, a small TypeScript sample with a `CLAUDE.md`; the finished result is beside it in `cache-meter-solution/`. You need Node.js for `npx` and Claude Code 2.1.287 or later.

```bash
cd demos/02-harness/06-hooks-mods/cache-meter
claude --version
```

---

## Step 1: Install the Mod from a Template Gallery

**Overview:** A mod is a plugin, but it does not have to come from a marketplace. The `claude-code-templates` gallery copies a mod's files straight into the project, where Claude Code picks it up on the next session start.

```bash
npx claude-code-templates@latest --mod observability/prompt-cache-control
```

**Expected Outcome:** Six files land under `.claude/skills/prompt-cache-control/`, and the installer names the plugin id Claude Code will load it under:

```text
✓ .claude-plugin/plugin.json
✓ README.md
✓ hooks/cache.ts
✓ hooks/hooks.json
✓ hooks/prompt-cache-control.tsx
✓ tests/cache.test.tsx
📁 Installed to: .claude\skills\prompt-cache-control/  (6 files)
   hooks/hooks.json  ->  { "modules": ["./prompt-cache-control.tsx"] }

🧪 Claude Code loads it as "prompt-cache-control@skills-dir" on the next session (after the workspace trust prompt).
```

The installer also prints an early-access warning about `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`. Ignore it: mods are on by default from Claude Code 2.1.287, and that version ignores the variable.

---

## Step 2: Read What the Mod Can Reach Before You Trust It

**Overview:** A mod runs with your permissions and is not sandboxed, so the review happens before the first session, not after. `claude plugin validate` reads the hooks module without running it and lists every event it handles, every mods API method it calls and every environment variable it reads.

```bash
claude plugin validate .claude/skills/prompt-cache-control
```

**Expected Outcome:** The validation passes and the three lines below are the whole inventory of what the mod does:

```text
  ❯ ./prompt-cache-control.tsx hooks: session.start, session.end, turn.step, command.run{command=cache}, ui.close, ui.press, ui.render{component=AbovePrompt}, ui.render{component=Pane}
  ❯ ./prompt-cache-control.tsx calls: $.clock.every, $.command.register, $.env.get, $.fs.read (via readSetting), $.session.cwd (via readSetting), $.session.usage, $.ui.close, $.ui.invalidate, $.ui.log, $.ui.open, $.ui.resolve, $.ui.status, $.ui.toast
  ❯ ./prompt-cache-control.tsx env reads: CLAUDE_CODE_PROMPT_CACHE_TTL, DISABLE_PROMPT_CACHING, DISABLE_PROMPT_CACHING_HAIKU, DISABLE_PROMPT_CACHING_OPUS, DISABLE_PROMPT_CACHING_SONNET, ENABLE_PROMPT_CACHING_1H, FORCE_PROMPT_CACHING_5M, HOME

✔ Validation passed
```

Read it as a reviewer: no `tool.call` hook, so it cannot hold or rewrite anything Claude runs, and no network call. The only file it reads is through `readSetting`, the settings lookup that decides the cache lifetime.

---

## Step 3: Run the Mod's Own Tests

**Overview:** `claude plugin test` runs the `.test.ts` files under `tests/` against the real mods runtime, with stubbed events and no sign-in. A mod you install should arrive with tests that pass on your Claude Code version, because the mods API can change between releases.

```bash
claude plugin test .claude/skills/prompt-cache-control
```

**Expected Outcome:** Every test passes on the version you run:

```text
(pass) observed lifetime > a hit more than 5 minutes later proves the 1-hour lifetime and sticks
(pass) which lifetime Claude Code asks for > follows the documented order: force 5m, CLAUDE_CODE_PROMPT_CACHE_TTL, setting, ENABLE_1H, account

 30 pass
 0 fail
Ran 30 tests across 1 file.
```

---

## Step 4: Watch the Meter Over Two Turns

**Overview:** The band above the prompt is drawn by the mod's `ui.render` hook on `AbovePrompt`, from the token counts every request reports. Two short turns are enough to see a warm cache.

Start a session and accept the workspace trust prompt, which is what lets Claude Code load the mod from `.claude/skills/`:

```bash
claude
```

Send these two prompts one after the other:

```text
Read src/types.ts and list the members of the ErrorCode union, one line each.
```

```text
Now read src/orders.ts and name the exported functions.
```

**Expected Outcome:** After each turn the band shows the hit rate, the tokens read from the cache, and a countdown to expiry. On a Claude subscription the lifetime is one hour:

```text
● cache ██████████ 99% read 84.8k ⏱ 59:18 1h · warm: keep going
                        wrote 369
                        new 2
```

A high read figure on the very first turn is normal: the system prompt and tool definitions were cached by earlier sessions in the same directory.

---

## Step 5: Break the Cache on Purpose

**Overview:** Every model has its own cache, so a model switch makes the next request write the whole history again. Claude Code warns you before it happens, and the mod's `/cache` pane shows the cost per turn.

Switch the model and confirm the dialog:

```text
/model haiku
```

```text
   Switch model?
   Your next response will be slower and use more tokens
   This conversation is cached for the current model. Switching to Haiku 4.5 means the full history gets re-read on your next message.
   ❯ 1. Yes, switch to Haiku 4.5
     2. No, go back
```

Send one more prompt, then open the pane:

```text
Read src/users.ts and name its exported functions.
```

```text
/cache
```

**Expected Outcome:** The pane's per-turn table shows the switch: turn 3 wrote 64.5k tokens to a fresh cache in its first request, so its hit rate drops to 50% while turn 2 sat at 100%.

```text
turn steps   read  wrote   new  hit
   1     2  84.8k  85.7k     4  50%
   2     2   172k    442     4 100%
   3     2  64.2k  64.5k    18  50%
```

`/model` also saved Haiku as your default for new sessions. Put it back before you leave:

```text
/model default
```

---

## Step 6: Pin the Mod's Options in a Settings File

**Overview:** The mod's `plugin.json` declares its options under `userConfig`. Mods read options from user settings, managed settings or a file passed with `--settings`, never from project settings, so a settings file you pass at start keeps the change inside this demo.

Create `cache-meter.settings.json` in `cache-meter/`:

```json
{
  "pluginConfigs": {
    "prompt-cache-control@skills-dir": {
      "options": {
        "ttl": "1h",
        "warnSeconds": 120,
        "compactAtTokens": 50000,
        "status": true
      }
    }
  }
}
```

The key is the full plugin id from Step 1. The installer's own hint prints `prompt-cache-control` without `@skills-dir`, and an option under that key is silently ignored.

Check it without a model call. In Git Bash, `MSYS_NO_PATHCONV=1` stops the shell from turning `/cache` into a Windows path:

```bash
MSYS_NO_PATHCONV=1 claude -p "/cache" --settings cache-meter.settings.json
```

```powershell
claude -p "/cache" --settings cache-meter.settings.json
```

**Expected Outcome:** The lifetime source changes from the default to your option:

```text
prompt-cache-control: 1h cache (the ttl option) · no request yet: the first one writes the cache · /cache stop closes
```

Start an interactive session with `claude --settings cache-meter.settings.json` and send any prompt. With `status: true` the meter also appears under the prompt:

```text
  ⚠ prompt-cache-control: cache 98% · 59:23
```

---

## Cleanup

The mod and the settings file live only in `cache-meter/`. Remove them to return the starter to its shipped state:

```bash
rm -rf .claude cache-meter.settings.json
```

```powershell
Remove-Item -Recurse -Force .claude, cache-meter.settings.json
```
