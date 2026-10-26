# EF Core: context registration and query patterns

## Context Registration

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("App")));
```

Connection string in `appsettings.json`:

```json
"ConnectionStrings": {
  "App": "Server=localhost;Database=mydb;Trusted_Connection=True;"
}
```

## Query Patterns

| Pattern | Code |
|---|---|
| Read all (no tracking) | `await db.Items.AsNoTracking().ToListAsync()` |
| Read by primary key | `await db.Items.FindAsync(id)` |
| Filtered read | `await db.Items.AsNoTracking().Where(i => i.Name == name).ToListAsync()` |
| Add and save | `db.Items.Add(entity); await db.SaveChangesAsync()` |
| Remove and save | `db.Items.Remove(entity); await db.SaveChangesAsync()` |

Always use `AsNoTracking()` for read-only queries to reduce memory overhead and avoid unintended change tracking.

**A nullable soft-delete flag is filtered with `!= true`, never `== false`.** A `bool? Deleted` column
is `NULL` on every row nobody explicitly marked, and `e.Deleted == false` excludes those in SQL and in
the InMemory provider alike. One aggregate picked each account's "latest" balance from 2016 because
only the old rows had `0` written: every current row was silently filtered out, and the result still
looked plausible. Check with `SELECT COUNT(*) ... WHERE Deleted IS NULL` before trusting `== false`,
and give the regression test one row with the flag left unset.

**A Guid stringified inside the query comes back uppercase on SQL Server.** `.Select(u =>
u.ModelId.ToString())` translates to a SQL `CONVERT`, and SQL Server renders `uniqueidentifier` in
upper case, while .NET's `Guid.ToString()` is lower case. Compared case-sensitively against ids that
came from .NET (a catalogue, a JSON payload), the match never fires and the code silently takes its
fallback branch: every agent run here used the first catalogue model instead of its configured one.
Select the `Guid`, then stringify after `ToListAsync`, or compare with
`StringComparison.OrdinalIgnoreCase`. The InMemory provider runs `ToString()` in .NET and cannot
reproduce this, so prove the fix against SQL Server: the live behaviour, or a query of the column.

## A period bucket keys on the header's date, never on a line's own date range

In any header/detail schema (invoice and lines, voucher and entries, order and items) the **detail row
usually carries its own dates** — a service period, a delivery window, a depreciation start. Those are
not the accounting period. The period belongs to the header.

```csharp
// WRONG: a document dated in August whose lines carry April service periods
// disappears from August entirely, and silently reappears in April.
from line in db.Lines
where line.StartDate.Year == year && line.StartDate.Month == month
select line

// RIGHT: join the header and key on its date
from line in db.Lines
join doc in db.Documents on line.DocumentId equals doc.Id
where doc.Date.Year == year && doc.Date.Month == month
select line
```

Why it survives review: both versions compile, both return plausible rows, and the **annual** total is
often identical because the misplaced amounts only move between months inside the year. It surfaces as
one report disagreeing with another, months after the fact, and only where a line's range crosses a year
boundary does the yearly figure move too.

Two checks that catch it:

- Find the existing reference implementation before writing a new aggregation and copy its date basis.
  In a codebase with both bases in use, one of them is the authority (usually whatever the
  statutory/financial engine uses) and the other is a bug waiting to be reported.
- Audit the data, not just the code: `GROUP BY MONTH(doc.Date), MONTH(line.StartDate)` and read the
  off-diagonal rows. An empty off-diagonal means no document has ever disagreed with its lines, so the
  defect is latent rather than absent, and the first multi-month line item will trigger it.

A corollary for the audit query itself: filtering headers on `doc.Date.Year` and details on
`line.StartDate.Year` and then intersecting drops precisely the mismatched rows, so an audit written that
way is blind to the one defect it exists to find.

## Moving an in-memory aggregate into SQL without changing the response

A rewrite from "load rows, then LINQ-to-Objects" to a server-side query is only a performance change
if the JSON a client receives stays byte-identical. Three traps change it silently, and InMemory tests
catch none of them because the InMemory provider translates nothing.

**Decimal scale is part of the bytes.** `System.Text.Json` writes a `decimal` with its scale: `0m`
serializes as `0`, a SQL Server `SUM` over `decimal(18,2)` comes back as `0.00`. LINQ `Sum` over no
rows or over `0m` literals returns scale 0; `COALESCE(SUM(...), 0.0)` returns scale 2. So:

- Keep a total in C# when its zero case is serialized (`"Unpaid":0` in the baseline means the sum
  must stay client-side, or be normalized).
- A server-side total is safe when an empty set produces no row: `GroupBy(v => v.IsIncome)` then
  `Sum` in C# over the returned groups. No rows, no group, `0m`.
- `?? 0m` inside arithmetic changes scale too: `x / 100 * (100 - 0m)` turns `123.45` into
  `123.4500`. Branch on the null (`q == null ? x : x / 100 * (100 - q.Quota)`) instead.

**Latest row per group has two translations with very different cost.**

```csharp
// Correlated TOP(1) per group key: 594 logical reads on a 1249-row table with no index on the key
.GroupBy(e => e.AccountId).Select(g => new { g.Key, Saldo = g.OrderByDescending(e => e.Date).Select(e => e.Saldo).First() })

// ROW_NUMBER() OVER (PARTITION BY ...) joined to the keys: 36 reads, same rows
.GroupBy(e => e.AccountId).Select(g => g.OrderByDescending(e => e.Date).First())
```

Projecting a scalar out of the ordered group produces a correlated subquery that rescans the table per
key; projecting the entity produces one window-function pass. Measure both shapes before choosing, on
the real data volume.

**Tie order is not guaranteed on either side.** The old `ToList()` then `OrderByDescending(...).First()`
broke ties by SQL scan order, which SQL Server never promises. Before claiming byte-identity, count
ties on the real data (`GROUP BY key, Date HAVING COUNT(*) > 1` on the latest date per key); zero ties
means the rewrite cannot pick a different row.

Proof, in order: capture the endpoint responses before any edit, rewrite, prove the new SQL is what
runs (`sys.dm_exec_query_stats` matched to the call's timestamp, since `dotnet watch` can keep serving
the old query), then `cmp` the responses. Cost comparison of old and new SQL:
`~/.claude/skills/sql-server/scripts/block-stats.py`.

Back to the index: [dotnet-efcore](dotnet-efcore.md)

## Validate before the write, never save and then delete

A rule that can only be checked after a derived value is computed (a schedule's start time after a
travel-time chain recompute, a total after a recalculation) tempts a "save, recompute, delete if it
broke" path. That is not a rollback: the row existed, other readers saw it, mails or audit entries
may already have fired, and a crash between the save and the delete leaves it behind.

1. Compute the hypothetical result in memory first: load the affected rows `AsNoTracking()`, overlay
   the insert or move, remove the delete, and run the same calculation the real write runs (one shared
   method with an `apply` flag, so preview and write cannot drift).
2. Reject on the preview, before `Add` and before any `SaveChanges`.
3. Only then perform the write and the real recompute.

Two traps that rule out the obvious alternatives:

- **The in-memory provider ignores transactions**, so a `BeginTransaction` + rollback design cannot be
  proven by the xUnit suite. Assert "no row persisted" against a preview instead.
- **Staging changes on the context and recomputing without saving fails** when the calculation's
  helpers (travel-time or geocode caches) call `SaveChanges` on the same `DbContext`: they commit the
  staged change as a side effect.

Proven in the bico planner, 2026-10-07: `ScheduleChainService.PreviewChainAsync` replaced a
compensating delete in `SetAssignment`, and Move and Delete fail the whole operation instead of
silently skipping a shift.
