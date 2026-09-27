# Seed rows: overwrite or preserve, and adding to a generator-owned table

## Overwrite or preserve is a decision, not a default

Delete-and-reinsert is the simpler script and is correct whenever the table is derived from a source
of truth in the repo and carries no user-entered state. Ask which it is. If the rows can be edited
through an application, the script must preserve those edits and idempotence comes from `MERGE` or
`WHERE NOT EXISTS` instead.

Note what overwriting discards. A C# seeder that matched an existing row by a stable key before
falling back to its label was doing so precisely to survive a rename; delete-and-reinsert drops that
behaviour, which is fine while nobody has used the application and wrong the day someone has. Record
that in the script's readme rather than in a commit message.

## Adding rows to a table a generator already owns

The trap is reaching for the generator. A script that regenerates a whole seed deletes every live row
to append yours: on one catalogue that meant dropping and rebuilding 48 rows in production to add 7.
The addition needs its own script, scoped to the new natural keys.

That script is two halves with a clean seam. The **judgement** half is per repo and belongs in the
repo: which keys are being added, which columns they have, which lookup each child row joins by. The
**deterministic** half is the same everywhere, so it lives here:

```bash
python <repo>/db/<project>/generate-<thing>-additions.py <key> [<key> ...] \
  | python ~/.claude/skills/dotnet-conventions/scripts/gen-additive-delta.py \
      --manifest - --out db/<project>/deltas/<date>-<thing>-additions.sql
```

`scripts/gen-additive-delta.py` takes a manifest (databases, parent table with its natural key and
rows, child tables with their foreign key and any natural-key lookups) and emits a script that is
guarded on `DB_NAME()` and on every table existing, transactional, inserts parents whose key is
absent, updates the same keys in place on a re-run, replaces child rows only for those parents,
throws on an unresolved lookup rather than writing `NULL`, and closes with one count `SELECT` per
table **restricted to those keys**. That last restriction is the point: a whole-table count proves the
run happened, a scoped count proves the scope.

Its own `--help` carries the manifest shape. Harvest the manifest from the repo's source of truth,
never by hand: the fields that decide ordering and membership are exactly the ones a hand-typed
manifest gets wrong.

Verify the same way as any delta, plus one extra check that only applies here: the totals of every
touched table must be **unchanged** by a second run, while the scoped counts still match.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
