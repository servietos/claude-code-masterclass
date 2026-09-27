# Storing a file in SQL: when to choose it, and the alternatives

## When to use

- One file belongs to one row, the file is small (single-digit MB), and you want it to back up,
  restore, replicate and delete with the row rather than needing a second system kept in sync.
- The deployment has no object store, or adding one buys nothing: an internal tool, a single box, a
  blue/green pair sharing one SQL Server.

Use [`azure-blob-storage`](azure-blob-storage.md) instead when files are large, numerous, streamed,
or served directly to browsers via a signed URL. The upload half of a multi-row import pipeline
(spreadsheet, PDF, OCR) is [`file-import-ingest`](file-import-ingest.md); this leaf is only about
where the bytes come to rest.

## Related

- [`dotnet-efcore`](dotnet-efcore.md) - entity configuration and query patterns.
- [`dotnet-controllers`](dotnet-controllers.md) - controller and CRUD endpoint shape.
- [`sql-delta-scripts`](sql-delta-scripts.md) - shipping the table where migrations are prohibited.
- [`azure-blob-storage`](azure-blob-storage.md) - the alternative when the file does not belong in the DB.

Back to the index: [sql-stored-files](sql-stored-files.md)
