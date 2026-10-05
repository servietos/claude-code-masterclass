# Guard Unrequested Commands with a Mod

A settings hook can refuse a command, but it cannot know whether you asked for it, so it either blocks work you wanted or lets through work you never asked for. You load a mod that remembers what you asked for in this session, watch it hold a destructive git command you never requested and let the same command through once you ask for it, then teach it a new family of commands with a test. You finish with a guard that pauses package publishing unless a recent prompt asked to publish.

------

Work in `guard-sandbox/`: the `intent-guard` mod and a `notes.md` to experiment on. The finished result is beside it in `guard-sandbox-solution/`. Nothing needs installing beyond Claude Code 2.1.287 or later.

```bash
cd demos/02-harness/06-hooks-mods/guard-sandbox
```

---

## Step 1: Read What the Guard Reaches

**Overview:** Before a mod sits between Claude and your shell, read its inventory. `claude plugin validate` lists the events it hooks, the mods API methods it calls, and the state it keeps between hooks.

```bash
claude plugin validate intent-guard
```

**Expected Outcome:** A `tool.call` hook, which is what lets it hold a command, plus `prompt.submit`, which is how it learns what you asked for:

```text
  ❯ types ./types/index.d.ts declares state: intent-guard.prompts, intent-guard.lastAnswer, intent-guard.held
  ❯ ./intent-guard.mjs hooks: session.start, prompt.submit, turn.complete, tool.call, ui.render{component=Pane}
  ❯ ./intent-guard.mjs calls: $.fs.read (via readSqlScripts), $.session.cwd, $.state.get, $.state.set, $.ui.ask, $.ui.close (via dropHeld), $.ui.open, $.ui.resolve
✔ Validation passed
```

`$.ui.ask` is the call that waits for you without spending the hook's time budget, and `$.fs.read` only reads the SQL scripts a database command points at.

---

## Step 2: Run the Guard's Tests

**Overview:** The tests fire prompts and shell commands at the mod with stubbed tools, so you can see the rules it enforces without risking anything. They are also the safety net for the change you make in Step 5.

```bash
claude plugin test intent-guard
```

**Expected Outcome:**

```text
 17 pass
 0 fail
Ran 17 tests across 1 file.
```

Open [`intent-guard/hooks/intent-guard.mjs`](guard-sandbox/intent-guard/hooks/intent-guard.mjs) and find `FAMILIES`. Each family pairs a `match` pattern for the command with an `intent` pattern for your words; a command is held only when it matches a family and none of your recent prompts matches that family's intent.

---

## Step 3: Watch It Hold a Command You Did Not Ask For

**Overview:** `git checkout -- <file>` throws away uncommitted work. The `git-discard` family's intent words are things like discard, revert and undo, so a prompt that only names the command does not count as asking for its effect.

Add a line to the end of `notes.md` so there is something to lose:

```markdown
- Unreleased: typo fixes.
```

Start a session with the guard loaded for this session only:

```bash
claude --plugin-dir intent-guard
```

Send this prompt:

```text
Run git checkout -- notes.md and report the result.
```

**Expected Outcome:** Claude calls Bash, and the guard holds the call before it runs. The Intent Guard pane opens beside the transcript with the reason, and a question waits for you:

```text
 ☐ Guard

│ Intent Guard held a command because you did not ask for it (discards git work). Run it?

❯ 1. Proceed
  2. Cancel
```

```text
 No request found for: discards git work
 Your last prompt: Run git checkout -- notes.md and report the result.
```

Choose **Cancel**. `notes.md` still carries your line. Where nobody can answer, as in `claude -p`, the guard denies instead of waiting, and Claude receives this as the tool result:

```text
Intent Guard held this command because the user did not ask for it (discards git work), and nobody could confirm it. Do not retry it or reach the same result another way; ask the user.
```

---

## Step 4: Ask for It and Watch It Pass

**Overview:** The same command passes once a recent prompt asks for its effect. That is the difference from a `PreToolUse` settings hook: the decision depends on the conversation, which only a mod that keeps state across hooks can see.

In the same session, send:

```text
Discard my uncommitted changes to notes.md with git checkout.
```

**Expected Outcome:** No question appears. Claude runs `git checkout -- notes.md`, and the line you added is gone:

```bash
git status --short notes.md
```

The command prints nothing, because `notes.md` matches the last commit again.

---

## Step 5: Teach the Guard a New Family

**Overview:** Publishing a package is as hard to undo as discarding work, and the guard does not know it yet. You add a family with a test, and because the session loaded the mod with `--plugin-dir`, Claude Code reloads it when the turn that changed it ends.

In the same session, send:

```text
In intent-guard/hooks/intent-guard.mjs, add a family to FAMILIES right before the db-write family:
- id "package-publish", label "publishes a package"
- match: npm, pnpm or yarn publish, dotnet nuget push, and twine upload
- intent: publish (any suffix), release, or ship
- messageScoped: true, so only the last few prompts count, the same as commit and push

In intent-guard/tests/intent-guard.test.ts, add two tests before "with nobody to ask the held command is denied", using the existing harness, start, say and sh helpers:
1. After the prompt "bump the version to 1.0.1", "npm publish --access public" is held: one question asked, nothing ran, and the deny text mentions "publishes a package".
2. After "bump the version to 1.0.1 and publish it", both "npm publish --access public" and "dotnet nuget push bin/Release/app.1.0.1.nupkg" run without a question.

Then run claude plugin validate intent-guard and claude plugin test intent-guard and show me both results.
```

**Expected Outcome:** The new family sits between `pr-merge` and `db-write`:

```diff
+  {
+    id: "package-publish",
+    label: "publishes a package",
+    match: (c) => /\b(npm|pnpm|yarn)\s+publish\b|dotnet\s+nuget\s+push\b|\btwine\s+upload\b/i.test(c),
+    intent: /\b(publish\w*|release|ship)\b/i,
+    messageScoped: true,
+  },
```

Validation still passes, and the test count grows by two:

```text
 19 pass
 0 fail
Ran 19 tests across 1 file.
```

Compare your result with [`guard-sandbox-solution/intent-guard/`](guard-sandbox-solution/intent-guard/hooks/intent-guard.mjs).

---

## Cleanup

Loading the mod with `--plugin-dir` writes generated type declarations into `intent-guard/.claude-plugin/types/`, which the mod's `.gitignore` already excludes. Discard your edits to the starter when you are done:

```bash
git restore intent-guard notes.md
```
