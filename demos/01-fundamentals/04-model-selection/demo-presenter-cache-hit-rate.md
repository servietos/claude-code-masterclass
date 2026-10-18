---
presents: demo-cache-hit-rate.md
budget: 4 min
beats: 4
---

# Present: Measure and Protect Your Cache Hit Rate

Four beats move `cache read` and `cache write` in a live session, from the first warm turn to the invalidations everyone causes by accident. The room walks away knowing which of their own actions rewrite the whole conversation, and that a mid-session CLAUDE.md edit changes nothing until the next `/clear`.

------

**No solution folder ships.** The run leaves `CACHE-NOTES.md` and an edited `CLAUDE.md` in `cache-lab/`; delete `CACHE-NOTES.md` and revert `CLAUDE.md` from git before the next run.

## Beats

### Beat 1: Three ordinary turns flip the ratio (1 min)

**Open:** [`cache-lab/src/types.ts`](cache-lab/src/types.ts) · [`cache-lab/src/orders.ts`](cache-lab/src/orders.ts)
**Say:** A cold session pays to write the cache; every turn after that should mostly be reading it. The turn that proves it is the one that reads nothing new.

```text
@src/types.ts @src/orders.ts

Summarize the Result type and how orders.ts uses it. Keep it to five sentences.

...

Without reading any new files: which module would you expect to need the most
changes if Money gained a third field, and what makes you say so?
```

**Result:** row 2 of `CACHE-NOTES.md`, labelled "three warm turns", carrying the read-to-write ratio as a single number.

**Gotcha:** write still climbing steeply by the third turn means something in the configuration is changing between turns.

### Beat 2: The model is part of the cache key (1 min)

**Open:** [Step 1: Break the Cache on Purpose](demo-cache-hit-rate.md#step-1-break-the-cache-on-purpose) · [`cache-lab/`](cache-lab)
**Say:** Model, effort level and fast mode all sit in the cache key, which is the part nobody guesses. Switching any of them mid-session throws away a prefix that was expensive to build.

```text
/model sonnet

...

Without reading any files, restate in two sentences what you said about
currency_mismatch earlier.

...

/usage

Add this as row 3 of CACHE-NOTES.md, labelled "after model switch". Compare the
write figure against row 2 and say what was actually rewritten.
```

**Result:** row 3 of `CACHE-NOTES.md`, written on a turn that read no files and produced two sentences, with write back up near the size of the whole conversation.

**Gotcha:** the tokens are identical and the cache misses anyway, because each model has its own cache.

### Beat 3: The mid-session CLAUDE.md edit is silently inert (1 min)

**Open:** [`cache-lab/CLAUDE.md`](cache-lab/CLAUDE.md) · the `## Conventions` result rule
**Say:** Project context is read once, at session start, and is then part of the cached prefix. Editing the file mid-session changes disk and nothing in the conversation.

```markdown
## Conventions

Every exported function takes a single options object and returns a discriminated result of the form `{ ok: true, value }` or `{ ok: false, error }`. Errors carry a snake_case code from the `ErrorCode` union. No function throws.
```

**Result:** the file on disk now says `{ status: "ok" }`, and the same session still quotes `{ ok: true }` and writes `getOrderStatus` to match it; after `/clear` it quotes the new rule.

**Gotcha:** there is no warning, which is why this costs people an afternoon.

### Beat 4: Compaction builds a prefix, rewinding returns to one (1 min)

**Open:** [`cache-lab/src/payments.ts`](cache-lab/src/payments.ts) · [Step 3: Choose Between `/compact` and `/rewind`](demo-cache-hit-rate.md#step-3-choose-between-compact-and-rewind)
**Say:** Both make a session shorter and their effect on the cache is opposite. One writes a history sharing no prefix with the old; the other truncates back to one already cached.

```text
@src/payments.ts

Explain capturedTotal and what happens when an order has payments in two
currencies.

Then, separately: I want to abandon this line of questioning entirely. Compare
/compact and /rewind for that purpose, in terms of what happens to the cached
prefix in each case. Which one should I reach for and why?
```

**Result:** row 5 of `CACHE-NOTES.md`, labelled "after compaction", plus an account of which half of it cost the time.

**Gotcha:** for abandoning a path `/rewind` is the cheap one; treating the two as interchangeable is the misreading.

## If the room asks

| Question | Answer |
|---|---|
| Is the dollar figure in `/usage` my bill? | On a subscription it is computed locally at list rates, so read the token counts and set the cost line aside. |
| Does editing a source file break the cache? | No. Reads append to the conversation, and Claude Code notes the change as a new message. |
| Do two terminals share a cache? | In the same directory yes, in different directories no, including two worktrees of one repository. |
