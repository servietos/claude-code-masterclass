# The blob table: DDL and the four schema decisions

## The blob lives in its own table, keyed on the owner's id

```sql
CREATE TABLE dbo.ItemFiles (
    ItemId      uniqueidentifier NOT NULL,
    FileName    nvarchar(260)    NOT NULL,
    ContentType nvarchar(100)    NOT NULL,
    FileSize    int              NOT NULL,
    Content     varbinary(max)   NOT NULL,
    CONSTRAINT PK_ItemFiles PRIMARY KEY (ItemId),
    CONSTRAINT FK_ItemFiles_Items FOREIGN KEY (ItemId)
        REFERENCES dbo.Items(Id) ON DELETE CASCADE
);
```

Four decisions, none of them cosmetic:

- **A separate table, not a column on `Items`.** `varbinary(max)` on the owning table is what makes
  every `SELECT *`, every list endpoint and every EF entity load drag megabytes it never reads. The
  side table means the blob is only ever touched by a query that names it.
- **The id is simultaneously the primary key and the foreign key.** One file per row is expressed by
  the schema rather than by a unique index bolted on afterwards, and there is no surrogate `FileId`
  for anyone to pass around.
- **`ON DELETE CASCADE`.** Deleting the owner disposes the bytes. Without it the file outlives the
  row and nothing ever collects it.
- **`FileSize` is stored, not derived.** A list needs the size; computing it from `DATALENGTH` in the
  projection is fine in raw SQL but is one more thing EF has to be persuaded not to materialise.

In a project that ships schema as hand-written deltas rather than EF migrations, this table arrives
as a delta script: see [`sql-delta-scripts`](sql-delta-scripts.md).

Back to the index: [sql-stored-files](sql-stored-files.md)
