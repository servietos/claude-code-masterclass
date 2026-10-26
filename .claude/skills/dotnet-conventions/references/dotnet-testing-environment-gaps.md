# What a Green Suite Cannot Prove

## A green suite proves only what its environment can express

The in-memory provider **has no schema**. It accepts any model the code declares, so a suite can be
fully green while the model expects a column, table or index that no real database has. The failure
then appears at runtime on the first query, with the build and the tests both reporting healthy.

This is not hypothetical. A session shipped a new `bool` property plus its fluent mapping, ran 626
green tests, and the running API would have failed on **every** query against that entity — the DDL
had never been applied. A second, worse case: two tables the code queried on every page load did not
exist in the target database at all, and nothing in the test suite could notice.

**Add a model-versus-schema check and run it before trusting a suite.** Walk
`dc.Model.GetEntityTypes()` for mapped tables, columns, CLR types and nullability, diff against
`INFORMATION_SCHEMA.COLUMNS` for the target database, and report both directions. Model-expects-but-
missing is a runtime failure waiting to happen; database-has-but-unmapped is harmless drift worth
knowing. Compare case-insensitively — SQL Server does not care and a casing difference is a false
positive.

Generalise the habit. For each suite, name how its environment differs from production and ask
whether that difference could conceal the bug class under test:

| Environment | Hides |
|---|---|
| In-memory EF provider | Schema drift, real FK and constraint behaviour, provider-specific SQL translation, `HasMaxLength` (a 200-character value saves into a 60-character column), and `DateTimeKind` round-trips through value converters (a property with no UTC converter still comes back `Utc`, so a missing converter and a JSON timestamp without `Z` both stay green) |
| The developer's own machine timezone | Anything reading `TimeZoneInfo.Local` or converting `DateTime` implicitly; a container with no `TZ` runs UTC |
| A `date` column read back as `DateTime` | Time-of-day precision, and a `Kind` mismatch between the write echo and a fresh read |
| A `WebApplicationFactory` whose test scheme authenticates every request | Every authorization decision under test: an "anonymous caller" assertion runs authenticated |

Where the difference is load-bearing, add one check that runs in the production shape rather than
broadening the unit suite: a schema diff, or a container run with the real `TZ` set.

Back to the index: [dotnet-testing](dotnet-testing.md)
