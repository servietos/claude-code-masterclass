# Storing a file IN the SQL database (varbinary(max) through EF Core)

Keep an uploaded file's bytes in the relational database next to the row that owns it, and serve
them back as a download, without letting the blob leak into every query that never reads it.

| You want to... | Read |
| --- | --- |
| Should this file's bytes live in the database at all, or in blob storage or an import pipeline? | [sql-stored-files-choosing](sql-stored-files-choosing.md) |
| What table do I create for the bytes, and why a side table with the owner's id as both PK and FK? | [sql-stored-files-schema](sql-stored-files-schema.md) |
| EF added a shadow key beside the PK, or I copied a HasOne/WithMany sibling config and the one-to-one broke. | [sql-stored-files-ef-mapping](sql-stored-files-ef-mapping.md) |
| How do I project the file metadata into a list DTO, read the bytes once, and replace an existing upload? | [sql-stored-files-queries](sql-stored-files-queries.md) |
| What do the POST upload (multipart, size-capped) and GET download (FileResult) actions look like? | [sql-stored-files-endpoints](sql-stored-files-endpoints.md) |
| How do I verify the stored file comes back with the right headers, format and byte count? | [sql-stored-files-verification](sql-stored-files-verification.md) |

A shared-PK
one-to-one needs both halves changed: `WithOne()`, and `HasForeignKey<TDependent>(...)` with the
**dependent** type as the generic argument.
