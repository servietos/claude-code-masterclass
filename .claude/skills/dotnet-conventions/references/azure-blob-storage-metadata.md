# Blob metadata that survives

## Blob metadata: make the file self-describing

Stamping the parent row's identity onto the blob means a lost or corrupted database row can be
rebuilt from the container alone. It is cheap, and it is the difference between an orphaned PDF and
a recoverable document. Three things break quietly.

**1. Metadata travels as HTTP headers, so values must be ASCII.** `Internetgebühren`, a newline, or
any accented supplier name will throw or corrupt. Encode on write, decode on read, and keep the
decode on the server so consumers never see the escaped form:

```csharp
metadata[key] = Uri.EscapeDataString(value);   // write
value = Uri.UnescapeDataString(metadata[key]); // read
```

Test it with a real umlaut. An ASCII placeholder proves nothing.

**2. Numbers must be invariant.** `ToString("F2", CultureInfo.InvariantCulture)`. A German-locale
server emits `50,45` otherwise, and the value is unparseable by anything downstream.

**3. Listing returns no metadata unless you ask for it.** `GetBlobsAsync()` omits it by default, so
every row comes back with an empty map while single-blob fetches look perfectly correct — a bug that
only ever surfaces in the UI:

```csharp
await foreach (var item in containerClient.GetBlobsAsync(new GetBlobsOptions { Traits = BlobTraits.Metadata }))
```

(The overload shape moves between SDK majors; on `Azure.Storage.Blobs` 12.28 it is `GetBlobsOptions`,
not the `(traits, states, prefix, ct)` positional form. A wrong guess here is a compile error, which
under `dotnet watch` means the app silently keeps serving the previous build.)

**4. Every copy/move/promote drops metadata unless it carries it.** A helper that re-uploads through
`UploadAsync` starts the destination blob with nothing, and the stage-then-promote path above is
exactly such a helper. Fetch the source metadata and pass it to the destination, and cover it with
its own test.

Keep the key set small and named by whoever owns the data. Identity keys (row id, document number,
date, original file name before any prefixing, ingestion origin) are what make matching possible;
everything else is convenience.

Back to the index: [azure-blob-storage](azure-blob-storage.md)
