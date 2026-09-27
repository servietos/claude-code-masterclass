# Column encryption in SQL Server from .NET

Passphrase column encryption whose plaintext stays recoverable from the database alone: scope, storage, C# mapping, the round trip, the silent traps, and the hand-run SQL.

The one rule that survives routing: **A wrong passphrase returns NULL, it does not throw.**

| You want to... | Read |
|---|---|
| Should this column be encrypted server-side at all, and why can an EF Core ValueConverter not do it? | [when-and-why](dotnet-column-encryption-when-and-why.md) |
| What columns and types does the SQL delta add, and which column wins when both plaintext and cipher exist? | [storage-shape](dotnet-column-encryption-storage-shape.md) |
| How do I mark a property encrypted, and what does adding a second encrypted property cost? | [attribute-mapping](dotnet-column-encryption-attribute-mapping.md) |
| How is the value actually encrypted on write and decrypted back through LINQ? | [read-write-paths](dotnet-column-encryption-read-write-paths.md) |
| The value reads back empty, or garbled, or a bad passphrase reports no error: which silent trap is this? | [traps](dotnet-column-encryption-traps.md) |
| What SQL do I hand over to recover the plaintext from the database alone, and how do I prove the round trip still holds? | [sql-recovery-and-verification](dotnet-column-encryption-sql-recovery-and-verification.md) |
