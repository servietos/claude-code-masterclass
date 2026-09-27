# EF Core: splitting one model across services

## Splitting one EF model across services

When a single entity model has to become two or three services (one database, several owners), the
boundary is already written down: it is the set of `HasOne<T>()` calls that cross the areas you want
to separate. Find them before moving a file:

```bash
for f in Configuration/*Configuration.cs; do
  echo -n "$f: "; grep -o "HasOne<[A-Za-z]*>" "$f" | sort -u | tr '\n' ' '; echo
done
```

An area whose configurations only reference their own types moves cleanly. Every reference that
points outside becomes one of two things, and never a deleted relationship:

- **A read-only mirror.** Declare the principal entity in the borrowing service with just the key and
  identifying columns, and map it `ToTable("X", "schema", t => t.ExcludeFromMigrations())`. The
  foreign key stays expressed, the table stays owned by one service, and no migration in the
  borrower tries to create it.
- **A soft link.** Keep the column, drop the constraint, and say so in writing. Only where the
  services will genuinely not share a database.

Guard the partition in the context rather than in review: override `OnModelCreating`, call
`ApplyConfigurationsFromAssembly`, then walk `modelBuilder.Model.GetEntityTypes()` and throw if any
entity is neither the tenant marker interface (`ITenantOwned`) nor on a short reviewed allow-list of
genuinely global tables. A model that cannot build is a partition that cannot silently regress.

Order of operations when the code moves between repositories: copy excluding `bin`/`obj`,
`diff -rq` the copy against the source, build the copy, and only then delete the source. Check
`git ls-files` on the source first: an untracked project has no history to fall back on, and that is
exactly the kind that turns out to hold the only copy of a schema.

Back to the index: [dotnet-efcore](dotnet-efcore.md)
