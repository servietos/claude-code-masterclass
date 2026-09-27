# Proving the file round trip still holds

## Proof it still holds

Round-trip one real file through the running server and check the headers and the bytes:

```bash
curl -s -F "file=@sample.png" http://localhost:5000/items/$ID/file
curl -sD - -o out.bin http://localhost:5000/items/$ID/file | grep -i content-disposition
file out.bin && stat -c %s out.bin
```

The header must name the stored filename twice (a plain `filename=` and an RFC 5987 `filename*=`),
`file` must report the real format rather than "data", and the byte count must equal the `FileSize`
the list endpoint reports. In the test suite, assert that the list DTO type has no `byte[]` member:
that is the invariant which silently rots when someone adds a field.

Back to the index: [sql-stored-files](sql-stored-files.md)
