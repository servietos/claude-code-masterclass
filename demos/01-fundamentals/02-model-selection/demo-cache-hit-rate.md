# Measure and Protect Your Cache Hit Rate

Prompt caching is what keeps a long session affordable, and the two counters in `/usage` are how you watch it work. You warm the cache on a small TypeScript codebase, break it on purpose with a model switch, and prove that a mid-session CLAUDE.md edit changes nothing until the next restart.

---

Work in `demos/01-fundamentals/02-model-selection/cache-lab` from a fresh session (`/clear` first); no solution folder ships, so your measured results table is `cache-lab/CACHE-NOTES.md`.

## Step 1: Break the Cache on Purpose

A healthy session reads far more than it writes, because each turn appends to a prefix that is already cached. A model switch throws that away: each model has its own cache, and the next request re-reads the entire conversation with no hits at all.

Start with a first turn that summarizes the two files:

```text
@src/types.ts @src/orders.ts

Summarize the Result type and how orders.ts uses it. Keep it to five sentences.
```

After that turn, ask:

```text
@src/users.ts

Which of these functions could return a currency_mismatch, and why?
```

Add a third turn that reads no new files:

```text
Without reading any new files: which module would you expect to need the most
changes if Money gained a third field, and what makes you say so?
```

Then run `/usage` (read should now be several times write) and record it as row 2 of `CACHE-NOTES.md`. Run `/model sonnet` and, as the next turn:

```text
Without reading any files, restate in two sentences what you said about
currency_mismatch earlier.
```

```text
/usage

Add this as row 3 of CACHE-NOTES.md, labelled "after model switch". Compare the
write figure against row 2 and say what was actually rewritten.
```

Expected Outcome: a third row where write jumps back up to roughly the size of the whole conversation, on a turn that read no files and produced two sentences. That number is the price of the switch, and it is why the topic readme says to pick your model at the top of a session.

## Step 2: Prove the Mid-Session CLAUDE.md Edit Is Inert

Editing CLAUDE.md mid-session keeps the cache intact, but the edit does not apply either, because the file was read once at session start and held in memory. Edit `CLAUDE.md` yourself, outside Claude, so the Conventions rule returns `{ status: "ok" }` where it said `{ ok: true }`, save it, then ask in the same session:

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

Expected Outcome: before the `/clear`, Claude quotes the old `{ ok: true }` rule and writes `getOrderStatus` to match it, even though the file on disk says otherwise; after it, Claude quotes the new rule. Record both as row 4, because the failure mode here is silent: there is no warning that your edit was ignored.

## Step 3: Choose Between `/compact` and `/rewind`

Both shorten the conversation, and they do opposite things to the cache. Compaction builds a new prefix; rewinding returns to one that is already cached.

```text
@src/payments.ts

Explain capturedTotal and what happens when an order has payments in two
currencies.

Then, separately: I want to abandon this line of questioning entirely. Compare
/compact and /rewind for that purpose, in terms of what happens to the cached
prefix in each case. Which one should I reach for and why?
```

Then run `/compact`, follow it with `/usage`, and add the result as row 5 of `CACHE-NOTES.md`, labelled "after compaction".

Expected Outcome: compaction replaces the history with a summary that shares no prefix with the old one, while rewinding truncates back to content the cache was built from. The summarization request reads the existing cache, so most of compaction's wall-clock time is generating the summary, which is why running it at a break between tasks costs you nothing you would have noticed.
