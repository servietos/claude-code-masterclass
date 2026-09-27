# Write path (post-SaveChanges UPDATE) and read path (HasDbFunction)

## The write path

Encryption cannot run in a value converter, so it runs as one parameterized statement issued after
`SaveChangesAsync` and inside the same transaction. Derive table, schema and key column from the EF
model so the helper stays entity-agnostic, and interpolate **only** model metadata, never request data:

```csharp
var sql = $"UPDATE [{schema}].[{table}] SET [{cipherColumn}] = ENCRYPTBYPASSPHRASE(@passphrase, @v0) " +
          $"OUTPUT INSERTED.[{cipherColumn}] WHERE [{keyColumn}] = @key;";
```

Read the `OUTPUT` back in the same round trip and throw if the returned cipher is `NULL`. Without that
check the write silently stores nothing (see the ceiling trap below) and the row reads back as empty.
Send the passphrase and every value as `SqlDbType.NVarChar`, never as an inferred `string` parameter.

## The read path

Map the SQL function once and let LINQ do the rest:

```csharp
public static string? DecryptDbValue(byte[]? cipher, string passphrase) =>
    throw new NotSupportedException("dbo.fn_DecryptDbValue is evaluated by SQL Server only.");

modelBuilder.HasDbFunction(typeof(Ctx).GetMethod(nameof(DecryptDbValue), [typeof(byte[]), typeof(string)])!)
    .HasName("fn_DecryptDbValue").HasSchema("dbo");
```

The body throws on purpose: it is a marker for the translator and must never execute client-side.
`DECRYPTBYPASSPHRASE` is deterministic and is allowed inside a scalar UDF, so the function is one line.

Back to the index: [dotnet-column-encryption](dotnet-column-encryption.md)
