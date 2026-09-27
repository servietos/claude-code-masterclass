# Five silent traps in passphrase column encryption

## Five traps, every one of them silent

**A wrong passphrase returns NULL, it does not throw.** So a naive `COALESCE` projection hands back
"no value" for every row and nothing anywhere reports an error. Carry a `HasCipher` flag through the
projection and throw a dedicated exception type when `HasCipher && value is null`. A dedicated type
matters: catching `InvalidOperationException` reports every EF connection and model failure as a bad
passphrase.

**Past roughly 3979 `nvarchar` characters `ENCRYPTBYPASSPHRASE` returns NULL without raising.** Guard
the plaintext length in C# before it reaches SQL, and guard it inside the write helper rather than
relying on callers, because a `SqlParameter` sized at `MaxLength` truncates silently and the `UPDATE`
still reports one row affected.

**The ciphertext is salted**, so two encryptions of the same plaintext differ. No equality search, no
unique index, no persisted computed column, no dedupe by value, and no test may assert on blob bytes.
Assert round-trips only.

**`CONVERT` must target `nvarchar`.** `CONVERT(varchar(...), DECRYPTBYPASSPHRASE(...))` returns
garbage, silently, with no error anywhere. Encrypt `nvarchar`, convert back to `nvarchar`, and expect a
reviewer to "tidy" it at some point.

**Portable across instances, not backwards across versions.** The ciphertext depends only on the
passphrase: no database master key, no service master key, so detach and attach anywhere works. But
SQL Server 2017+ writes AES-256 (header `0x02000000`) while 2016 and earlier used Triple DES, so
restoring forward is fine and backward is not. That caveat travels with the recovery statement, not
just with the code.

Back to the index: [dotnet-column-encryption](dotnet-column-encryption.md)
