# Hand-run SQL: the recovery statement and the verification checks

## The recovery statement

This is the deliverable the whole design exists for. Hand it over with its conditions:

```sql
SELECT s.[Name],
       COALESCE(s.[Password],
                CONVERT(nvarchar(4000), DECRYPTBYPASSPHRASE(N'<passphrase>', s.[PasswordCipher]))) AS [Plain]
FROM [dbo].[Secrets] AS s;
```

A `NULL` result where the cipher column is non-`NULL` means the passphrase is wrong, not that the row
is empty. Say that explicitly wherever the statement is published, because the two are indistinguishable
at the SQL layer.

## Verifying it still holds

Run these against a scratch database, never the live one:

```sql
DECLARE @p nvarchar(500) = N'Grüße-€-123';
DECLARE @c varbinary(8000) = ENCRYPTBYPASSPHRASE(N'key', @p);
SELECT CASE WHEN CONVERT(varbinary(1000), CONVERT(nvarchar(4000), DECRYPTBYPASSPHRASE(N'key', @c)))
             = CONVERT(varbinary(1000), @p) THEN 'BINARY-IDENTICAL' ELSE 'MISMATCH' END;
```

Compare binaries, not console output: `sqlcmd` mangles non-ASCII on display and a correct round trip
looks broken. Then prove the boundary in the application: a row written before the change still reads
its plaintext and still has a `NULL` cipher, and a row written after has a `NULL` plaintext column and
a non-`NULL` cipher. That pair is the receipt for "encrypt new values, never touch existing records",
and it is the one check worth running after every schema change to the table.

**A failure path that cannot fire reports success.** Before trusting the wrong-passphrase guard, assert
that at least one row actually carries ciphertext. With zero encrypted rows, every passphrase including
a single letter passes, because no decrypt ever runs.

Back to the index: [dotnet-column-encryption](dotnet-column-encryption.md)
