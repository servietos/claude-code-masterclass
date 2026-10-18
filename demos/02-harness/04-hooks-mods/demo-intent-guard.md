# Guard Unrequested Commands with a Mod

A settings hook can refuse a command, but it cannot know whether you asked for it, so it either blocks work you wanted or lets through work you never asked for. You load a mod that remembers what you asked for in this session, watch it hold a destructive git command you never requested and let the same command through once you ask for it, then teach it a new family of commands with a test.

------

Work in `guard-sandbox/`: the `intent-guard` mod and a `notes.md` to experiment on; the finished result is beside it in `guard-sandbox-solution/`.

## Step 1: Watch It Hold a Command You Did Not Ask For

**Overview:** Each family in `FAMILIES` in [`intent-guard.mjs`](guard-sandbox/intent-guard/hooks/intent-guard.mjs) pairs a `match` pattern for the command with an `intent` pattern for your words, and a command is held only when it matches a family and none of your recent prompts matches that family's intent. The `git-discard` family's intent words are things like discard, revert and undo, so a prompt that only names `git checkout -- <file>` does not count as asking for its effect.

Add `- Unreleased: typo fixes.` to the end of `notes.md` so there is something to lose, then start a session with the guard loaded for this session only and send the prompt:

```bash
claude --plugin-dir intent-guard
```

```text
Run git checkout -- notes.md and report the result.
```

**Expected Outcome:** Claude calls Bash, and the guard holds the call before it runs. The Intent Guard pane opens beside the transcript with the reason, and a question waits for you:

```text
│ Claude wants to run `git checkout -- notes.md` in ...\guard-sandbox, which discards git work. Intent Guard held it because none of your recent prompts asked for that: run it?

❯ 1. Proceed
  2. Cancel
```

Choose **Cancel**: `notes.md` still carries your line. Where nobody can answer, as in `claude -p`, the guard denies the call and tells Claude to ask the user.

## Step 2: Ask for It and Watch It Pass

**Overview:** The same command passes once a recent prompt asks for its effect. That is the difference from a `PreToolUse` settings hook: the decision depends on the conversation, which only a mod that keeps state across hooks can see.

In the same session, send:

```text
Discard my uncommitted changes to notes.md with git checkout.
```

**Expected Outcome:** No question appears. Claude runs `git checkout -- notes.md`, and `git status --short notes.md` prints nothing, because `notes.md` matches the last commit again.

## Step 3: Teach the Guard a New Family

**Overview:** Publishing a package is as hard to undo as discarding work, and the guard does not know it yet. In the same session you add a family with a test, and because the session loaded the mod with `--plugin-dir`, Claude Code reloads it when the turn that changed it ends.

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

**Expected Outcome:** The new family sits between `pr-merge` and `db-write`, validation still passes, and the test count grows from 17 to 19:

```diff
+  {
+    id: "package-publish",
+    label: "publishes a package",
+    match: (c) => /\b(npm|pnpm|yarn)\s+publish\b|dotnet\s+nuget\s+push\b|\btwine\s+upload\b/i.test(c),
+    intent: /\b(publish\w*|release|ship)\b/i,
+    messageScoped: true,
+  },
```
