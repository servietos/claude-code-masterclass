# Column encryption: when to use it, and why not a ValueConverter

## When to use

Encrypting individual columns (a password, a token, a bank detail) in SQL Server from .NET, when the
plaintext must be recoverable **from the database alone**: attach the file to a fresh instance, supply
a passphrase, paste one statement, read the value. No application, no key vault, no certificate.

Triggers: "encrypt a field in the db", "column encryption", "DbEncrypted", "ENCRYPTBYPASSPHRASE",
"DECRYPTBYPASSPHRASE", "decrypt with only the database", "encrypt new values only".

Not this leaf: Always Encrypted and TDE (both are SQL Server features with their own key management,
and neither gives you a paste-one-statement recovery path), or hashing a password you never read back.

## The decision that drives everything else

The obvious .NET approach is an EF Core `ValueConverter`. **It is unusable the moment recovery must
work from the database alone**, because the converter encrypts in .NET and `DECRYPTBYPASSPHRASE`
cannot decrypt .NET AES. There is no T-SQL that reads an arbitrary AES-CBC blob either, so the
requirement forces the crypto server-side and every other decision follows from that:

| Requirement | Consequence |
|---|---|
| Recover with SQL alone | `ENCRYPTBYPASSPHRASE` on write, in a parameterized `UPDATE` |
| Read back through the ORM | A SQL scalar function mapped with `HasDbFunction`, used in the LINQ projection |
| Never migrate existing rows | A second column beside the old one, and a read-order rule |

If recovery from the database alone is *not* a requirement, use a value converter and stop reading:
it is simpler, needs no round trip, and does not carry the traps below.

Back to the index: [dotnet-column-encryption](dotnet-column-encryption.md)
