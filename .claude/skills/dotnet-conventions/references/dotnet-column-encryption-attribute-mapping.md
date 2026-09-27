# The DbEncrypted attribute and its companion properties

## Making it attribute-driven

An attribute plus a naming convention keeps the mechanism generic. For a property `P` carrying
`[DbEncrypted(maxLength)]`:

| Aspect | Rule |
|---|---|
| `P` | `Ignore()`d in the model: an unmapped, in-memory plaintext carrier |
| `{P}Legacy` | `string?` with a `private set`, mapped to column `P` |
| `{P}Cipher` | `byte[]?` with a `private set`, mapped to column `{P}Cipher` |
| Read | `{P}Legacy ?? DecryptFn({P}Cipher, passphrase)` in the projection |
| Write | one `UPDATE` per entity after `SaveChangesAsync`, inside the same transaction |

`private set` is what makes "plaintext never reaches a persisted column, even transiently" structural
rather than a promise: no code outside the entity can assign the legacy column, so EF writes `NULL`.

Adding a second encrypted property later costs the attribute, the two companion properties, and one
delta adding its cipher column. No new C#. No convention can add a column to a database that forbids
migrations, so the delta is not optional.

Back to the index: [dotnet-column-encryption](dotnet-column-encryption.md)
