---
presents: demo-intent-guard.md
budget: 5 min
beats: 4
---

# Present: Guard Unrequested Commands with a Mod

A mod can hold a tool call until a person answers, and it can decide from the conversation rather than the command alone. Four beats: the family that defines risk, the held call, the same call passing once asked, and a new family with its tests.

------

## Beats

### Beat 1: a family is a command pattern paired with an intent pattern (1 min)

**Open:** [`intent-guard.mjs`](guard-sandbox/intent-guard/hooks/intent-guard.mjs) · `FAMILIES`, the `git-discard` entry
**Say:** A command is held only when it matches a family and none of your recent prompts matches that family's intent. The words that count are the effect, not the command name.

```javascript
    id: "git-discard",
    label: "discards git work",
    match: (c) => /git\s+(-C\s+\S+\s+)?(checkout\s+(--|\.)|restore\b|stash\b(?!\s+(list|show))|reset\s+--hard|clean\s+-\w*f|branch\s+-D)|git\s+(-C\s+\S+\s+)?push\s+.*(--force|\s-f\b)/i.test(c),
    intent: /\b(revert|undo|discard|reset|restore|stash|throw away|roll\s?back|force|verwerf\w*|r(ü|ue)ckg(ä|ae)ngig|zur(ü|ue)cksetz\w*)\b/i,
```

**Result:** `claude plugin validate intent-guard`, with `tool.call` and `prompt.submit` as the two hooks that do the work

```text
  ❯ ./intent-guard.mjs hooks: session.start, prompt.submit, turn.complete, tool.call, ui.render{component=Pane}
  ❯ ./intent-guard.mjs calls: $.fs.read (via readSqlScripts), $.session.cwd, $.state.get, $.state.set, $.ui.ask, $.ui.close (via dropHeld), $.ui.open, $.ui.resolve
✔ Validation passed
```

**Gotcha:** "checkout" is not an intent word, so "Run git checkout -- notes.md" names the command without asking for its effect.

### Beat 2: holding a call means answering it later, or denying it (1.5 min)

**Open:** [`intent-guard.mjs`](guard-sandbox/intent-guard/hooks/intent-guard.mjs) · the `tool.call` hook, `$.ui.ask` · [`notes.md`](guard-sandbox/notes.md)
**Say:** The hook does not call `next` until you choose. Proceed passes the call on; anything else returns a `deny` that Claude reads as the tool result.

```javascript
      const who = item.agentId ? `Subagent ${item.agentId}` : "Claude";
      const where = isShell && cwd ? ` in ${cwd}` : "";
      const question = `${who} wants to run \`${brief(item.command, isShell, e.tool)}\`${where}, which ${item.reasons.join(" and ")}. Intent Guard held it because none of your recent prompts asked for that: run it?`;
      const choice = await $.ui.ask(question, { header: "Guard", options: ["Proceed", "Cancel"] });
      if (choice === "Proceed") return next(e);
      return { deny: `Intent Guard: the user pressed ${JSON.stringify(choice)} instead of Proceed for this command. It was held because ${why}. Do not retry it or reach the same result another way; ask the user.` };
```

**Result:** the question in the interactive session, with the Intent Guard pane open beside it and `notes.md` untouched

```text
│ Claude wants to run `git checkout -- notes.md` in ...\guard-sandbox, which discards git work. Intent Guard held it because none of your recent prompts asked for that: run it?

❯ 1. Proceed
  2. Cancel
```

**Gotcha:** under `claude -p` nobody can answer, so `$.ui.ask` rejects and the `catch` denies; a guard that waits has to choose a side when no person is there.

### Beat 3: the same command passes once a prompt asks for its effect (1 min)

**Open:** [`intent-guard.mjs`](guard-sandbox/intent-guard/hooks/intent-guard.mjs) · `prompt.submit` and the `unrequested` filter
**Say:** The prompts live in mod state, written by one hook and read by another. A settings hook starts fresh on every event and has no such memory.

```javascript
    const { value: prompts = [] } = await $.state.get(promptsRef);
    const unrequested = risky.filter((f) => !asked(f, prompts));
    if (unrequested.length === 0) return next(e);
```

**Result:** after "Discard my uncommitted changes to notes.md with git checkout." the call runs with no question, recorded headless as

```text
TOOL_USE Bash {"command": "git checkout -- notes.md", "description": "Discard uncommitted changes to notes.md"}
RESULT (Bash completed with no output)
```

**Gotcha:** commit, push, merge and test runs are message-scoped, so only the last three prompts count for them, not the whole session.

### Beat 4: a new family ships with the tests that pin it (1.5 min)

**Open:** [`tests/intent-guard.test.ts`](guard-sandbox-solution/intent-guard/tests/intent-guard.test.ts) · "an unrequested package publish is held"
**Say:** The change Claude makes reloads at the end of the turn, because the session loaded the folder with `--plugin-dir`. The tests are what make it safe to keep.

```diff
+  {
+    id: "package-publish",
+    label: "publishes a package",
+    match: (c) => /\b(npm|pnpm|yarn)\s+publish\b|dotnet\s+nuget\s+push\b|\btwine\s+upload\b/i.test(c),
+    intent: /\b(publish\w*|release|ship)\b/i,
+    messageScoped: true,
+  },
```

**Result:** [`intent-guard.mjs`](guard-sandbox-solution/intent-guard/hooks/intent-guard.mjs) in the solution, and `claude plugin test intent-guard` grown from 17 to 19

```text
 19 pass
 0 fail
Ran 19 tests across 1 file.
```

**Gotcha:** a test that passes `next(e)` through needs a stub for that event, which is why the shared `harness` answers every `tool.call` itself.

## If the room asks

| Question | Answer |
|---|---|
| Why not a `PreToolUse` hook? | A settings hook sees only the command; deciding whether you asked for it needs the prompts, which only a mod keeps across hooks. |
| Does the hold spend the hook's time budget? | No, waiting inside `$.ui.ask` costs no budget; a `$.clock.sleep` poll would and gets the call through after the budget runs out. |
| What if the guard throws? | A hook that throws is skipped and the call runs, so the deny path avoids calls that can throw and UI calls are best effort. |
| Is this a permission system? | No, it is a safety net; an absolute block belongs in `permissions.deny`, which bypass mode still honours. |

## Runs live instead

A learner edits `notes.md`, gets the question themselves and has Claude write the new family and its tests: [Guard Unrequested Commands with a Mod](demo-intent-guard.md).
