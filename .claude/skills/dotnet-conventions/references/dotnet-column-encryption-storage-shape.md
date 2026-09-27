# Cipher column shape and the read-order rule

## Storage shape and the read-order rule

Keep the existing plaintext column, never write it again, and add a cipher column beside it. Old rows
are then correct by construction, with no migration and no `UPDATE` anywhere in the delta:

```
Password       IS NOT NULL -> Password                                        (legacy row)
PasswordCipher IS NOT NULL -> CONVERT(nvarchar(4000), DECRYPTBYPASSPHRASE(@k, PasswordCipher))
both NULL                  -> NULL                                            (no value)
```

Column type is `varbinary(8000)`, never `varbinary(max)`: `ENCRYPTBYPASSPHRASE` *returns*
`varbinary(8000)`, so `max` can never be filled and only hides the ceiling. Measured size is
`20 + ceil((2n+9)/16)*16` bytes for an `nvarchar(n)` input (4-byte version header, 16-byte IV,
AES-256 blocks).

Back to the index: [dotnet-column-encryption](dotnet-column-encryption.md)
