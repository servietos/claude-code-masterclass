# Measure and Protect Your Cache Hit Rate

Prompt caching is what keeps a long session affordable, and the two counters in `/usage` are how you watch it work. You warm the cache on a small TypeScript codebase, break it on purpose with a model switch, and prove that a mid-session CLAUDE.md edit changes nothing until the next restart. You finish with a measured results table and a session-discipline section written into the file that survives the session.

---

## Demo Files

Work directly in the starter. It is a dependency-free TypeScript sample with no build step and nothing to install: its only job is to be large enough that reading it moves the token counters.

```bash
cd demos/01-fundamentals/05-prompt-caching/cache-lab
claude
```

| File | What it represents |
|------|--------------------|
| `CLAUDE.md` | The project context layer, read once at session start; Step 4 edits it |
| `src/types.ts` | The shared file every module imports, so every read pulls it in |
| `src/orders.ts` | A domain module with enough surface to be worth reading twice |
| `src/users.ts` | A second module, used to add conversation history without changing the prefix |
| `src/payments.ts` | A third module, kept in reserve for the post-compaction turn |
| `CACHE-NOTES.md` | Created in Step 1; your measured results table |

Run this on a fresh session. If you have been working in this directory already, `/clear` first, because the numbers only make sense from a cold start.

---

## Step 1: Read the Meters Before You Touch Anything

Overview: Every later step is a before-and-after comparison, so the first job is a cold baseline and a clear idea of what each number counts. Read the meters now, while the conversation is still one turn long.

Research / Planning / Discussion:

```text
Run /usage and /context and tell me what each panel reports right now.

For /usage specifically: explain what "cache read" and "cache write" count on a
single turn, and which of the two you would expect to dominate in a healthy
session. Then predict what happens to each number on my next message if I
change nothing about the configuration.

Do not change any settings, and do not read any project files yet.
```

Finding: The useful answer separates the two counters cleanly: creation is what was written to the cache this turn, read is what was served from it. Reject any explanation that treats them as a single hit-rate percentage, and reject any figure that is not visible on your own screen. On a subscription the dollar total is computed locally at list rates and is not your bill, so use the token counts, not the cost line.

Recipe:

```text
Create CACHE-NOTES.md with a table with these columns: step, what I did,
cache read, cache write, and what I expected.

Fill in row 1 from the /usage output we just looked at, labelled "cold start".
Leave the remaining rows empty. Do not read any source files while doing this.
```

Expected Outcome: A `CACHE-NOTES.md` with one filled row showing a low read figure and a write figure covering the system prompt and project context. This is the only turn in the demo where creation is legitimately larger than read.

---

## Step 2: Warm the Cache and Watch the Ratio Flip

Overview: A healthy session reads far more than it writes, because each turn appends to a prefix that is already cached. Build three ordinary turns of history and confirm the ratio moves in the expected direction.

Research / Planning / Discussion:

```text
@src/types.ts @src/orders.ts

Summarize the Result type and how orders.ts uses it. Keep it to five sentences.
```

Then, as separate turns:

```text
@src/users.ts

Which of these functions could return a currency_mismatch, and why?
```

```text
Without reading any new files: which module would you expect to need the most
changes if Money gained a third field, and what makes you say so?
```

Finding: Run `/usage` after the third turn. Read should now be several times write, because the two file reads and both answers are sitting in a prefix that every subsequent turn reuses. If write is still climbing steeply turn over turn, something in your configuration is changing between turns, and the invalidation table in the topic readme is the list to check.

Recipe:

```text
/usage

Add this as row 2 of CACHE-NOTES.md, labelled "three warm turns". Include the
read-to-write ratio as a single number, and say in one line why the third turn
cost almost nothing despite the conversation being longer than ever.
```

Expected Outcome: A second row where read clearly exceeds write. The third turn is the point: it read no files at all, yet it still carried the whole history, and almost all of that history was served from cache.

---

## Step 3: Break the Cache on Purpose

Overview: A model switch feels free because nothing visible changes. Measure it, because each model has its own cache and the next request re-reads the entire conversation with no hits at all.

Research / Planning / Discussion:

```text
I am about to run /model and switch to a different model, then ask a question
that reads no new files.

Predict what happens to cache read and cache write on that first request after
the switch, and explain why the content being identical does not help. Then tell
me one other action from this session that would have the same effect.
```

Finding: Expect the answer to name the cache key rather than the token count: the model is part of the key even though it is not part of the prompt text. A strong answer names a second invalidator that actually applies here, such as an effort change or turning on fast mode, rather than listing every entry in the table.

Recipe:

```text
/model sonnet
```

Then, as the next turn:

```text
Without reading any files, restate in two sentences what you said about
currency_mismatch earlier.
```

Then measure:

```text
/usage

Add this as row 3 of CACHE-NOTES.md, labelled "after model switch". Compare the
write figure against row 2 and say what was actually rewritten.
```

Expected Outcome: A third row where write jumps back up to roughly the size of the whole conversation, on a turn that read no files and produced two sentences. That number is the price of the switch, and it is why the topic readme says to pick your model at the top of a session.

---

## Step 4: Prove the Mid-Session CLAUDE.md Edit Is Inert

Overview: This is the behaviour that most often wastes an afternoon. Editing CLAUDE.md mid-session keeps the cache intact, but the edit does not apply either, because the file was read once at session start and held in memory.

Research / Planning / Discussion:

```text
Read CLAUDE.md and quote the rule about how exported functions return results.

Then, before I change anything: if I edit that rule on disk right now and ask
you again in the next turn, will you answer with the old rule or the new one?
Explain which layer CLAUDE.md sits in and when it is read.
```

Finding: A correct answer says the old rule, and ties it to the project context layer being loaded at session start. If the answer promises to pick up the change, treat that as the hypothesis to falsify in the recipe below, which is more instructive than a correct prediction.

Recipe:

Edit `CLAUDE.md` yourself, outside Claude, and change the Conventions rule so results are returned as `{ status: "ok" }` instead of `{ ok: true }`. Save the file. Then ask, in the same session:

```text
Quote the CLAUDE.md rule about how exported functions return results, exactly as
it reads. Then add a getOrderStatus function to @src/orders.ts that follows it.
```

Then start a fresh session in the same folder and ask the same question again:

```text
/clear

Quote the CLAUDE.md rule about how exported functions return results, exactly as
it reads.
```

Expected Outcome: Before the `/clear`, Claude quotes the old `{ ok: true }` rule and writes `getOrderStatus` to match it, even though the file on disk says otherwise. After the `/clear`, it quotes the new rule. Record both in `CACHE-NOTES.md` as row 4, because the failure mode here is silent: there is no warning that your edit was ignored.

---

## Step 5: Choose Between `/compact` and `/rewind`

Overview: Both shorten the conversation, and they do opposite things to the cache. Compaction builds a new prefix; rewinding returns to one that is already cached.

Research / Planning / Discussion:

```text
@src/payments.ts

Explain capturedTotal and what happens when an order has payments in two
currencies.

Then, separately: I want to abandon this line of questioning entirely. Compare
/compact and /rewind for that purpose, in terms of what happens to the cached
prefix in each case. Which one should I reach for and why?
```

Finding: The distinction to look for is that compaction replaces the history with a summary that shares no prefix with the old one, while rewinding truncates back to content the cache was built from. If the answer treats them as interchangeable ways to save context, ask specifically what the next request's prefix looks like in each case.

Recipe:

```text
/compact
```

Then, as the next turn:

```text
/usage

Add this as row 5 of CACHE-NOTES.md, labelled "after compaction". Then explain
which part of compaction actually cost time: generating the summary, or the
turn that followed it.
```

Expected Outcome: A fifth row and a correct account of where the cost sat. The summarization request shares your prefix, so it reads the existing cache rather than reprocessing everything; the turn afterwards rebuilds the conversation layer for a much shorter history. Most of compaction's wall-clock time is generating the summary, which is why running it at a break between tasks costs you nothing you would have noticed.

---

## Step 6: Encode the Discipline Where It Will Be Read

Overview: Everything measured so far is a habit, not a setting, and habits under deadline need to be written down. Put the rules into CLAUDE.md so they load at the start of every future session in this project.

Research / Planning / Discussion:

```text
Read CACHE-NOTES.md.

Which of the five rows represents money I could have saved by working
differently, and which represent unavoidable costs? Be specific: name the row
and the alternative action.

Then tell me which of your recommendations would be invisible to someone reading
only the source code, and therefore belongs in CLAUDE.md rather than a comment.
```

Finding: The rows worth acting on are the model switch and the inert edit; the cold start is unavoidable and compaction is a deliberate trade. Push back on any recommendation that amounts to "use the cache more", because the cache is automatic and the only lever is which actions you avoid mid-task.

Recipe:

```text
Add a "## Session discipline" section to CLAUDE.md with:

- Pick the model and effort level in the first turn of a session, never mid-task.
- Edits to this file take effect on the next /clear, /compact or restart. Restart
  after changing it rather than assuming the new rule is live.
- Prefer /rewind over /compact when abandoning a path, because it returns to a
  cached prefix.
- Run /compact at a break between tasks, not in the middle of one.
- Delegate high-volume reading to a subagent: it builds its own cache and returns
  only a summary, leaving this conversation's prefix intact.

Keep every line checkable, then show me the section you wrote.
```

Expected Outcome: A `## Session discipline` section in `cache-lab/CLAUDE.md` grounded in your own five rows, with `CACHE-NOTES.md` as the evidence behind it. Start a fresh session and ask Claude to switch models mid-task; it should name the cache cost before doing it.

---

## Summary

You read the two counters that actually report caching, warmed a prefix across three turns and watched read overtake write, then paid for a model switch and saw the whole conversation rewritten on a turn that read nothing. You proved that a mid-session CLAUDE.md edit is silently inert and that `/clear` is what applies it. You separated compaction from rewinding by what each does to the prefix, and wrote the resulting habits into the file that loads at session start.

The one lever the demo did not spend is scope. Sessions in different directories build different prefixes and miss each other's cache, including worktrees of the same repository, which is worth remembering when you reach [08: Git Worktrees](../08-git-worktrees/demo-worktrees-intro.md).

Continue with [Route Tasks to the Cheapest Model That Still Works](../06-model-selection/demo-model-routing.md), which puts a price on the model switch you just measured the cache cost of.

