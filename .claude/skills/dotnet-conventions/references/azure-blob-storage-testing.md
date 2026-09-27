# Mocking BlobStorageService

## Testing

Mock `BlobStorageService` the same way the AI chat client is mocked in `file-import-ingest.md` —
`Substitute.ForPartsOf`, since every member is `virtual` on a concrete class, not an interface:

```csharp
// src/my-api.Tests/ImportDocumentTests.cs
var blob = Substitute.ForPartsOf<BlobStorageService>((Azure.Storage.Blobs.BlobServiceClient)null!);
```

**Important gotcha**: `ForPartsOf` calls the *real* method body for anything you haven't explicitly
stubbed with `.Returns(...)`. Since the substitute's `client` is `null` ("disabled"), an unstubbed
call runs the real guarded body and throws `BlobStorageDisabledException` — correct for the
"storage unavailable" tests, but happy-path tests must stub success explicitly first:

```csharp
// src/my-api.Tests/ImportDocumentTests.cs
private static void StubBlobSuccess(BlobStorageService blob)
{
    blob.UploadAsync(Arg.Any<string>(), Arg.Any<string>(), Arg.Any<Stream>(), Arg.Any<string>()).Returns(Task.CompletedTask);
    blob.MoveAsync(Arg.Any<string>(), Arg.Any<string>(), Arg.Any<string>(), Arg.Any<string>()).Returns(Task.CompletedTask);
}
```

What to assert:

- **Stage on ingest**: `await blob.Received(1).UploadAsync("import-documents", Arg.Is<string>(n => n.StartsWith("staging/") && n.Contains(originalFileName)), Arg.Any<Stream>(), contentType);` and `draft.SourceDocument` is populated.
- **Persist on confirm**: `await blob.Received(1).MoveAsync("import-documents", stagingBlobName, Arg.Is<string>(n => n.StartsWith($"{kind}/")), contentType);` and exactly one `ImportDocument` row exists with the expected `Kind`/`FileName`/`ParentId`.
- **Non-fatal blob failure**: `blob.MoveAsync(...).Throws(new InvalidOperationException(...));` then confirm — the row upsert result is unaffected and no `ImportDocument` row was inserted.
- **No `SourceDocument`** (staging never happened, e.g. it failed on ingest): confirm skips retention entirely — `blob.DidNotReceive().MoveAsync(...)`, no `ImportDocument` row.
- **Download endpoint**: stub `blob.DownloadAsync(container, blobName).Returns((stream, contentType))`, seed the `ImportDocument` row directly, call the controller action, assert the returned `FileStreamResult.FileStream`/`ContentType`/`FileDownloadName`.

Never hit real Azure Storage in tests — there is no integration-test tier for this unless the project has explicitly added one.

Back to the index: [azure-blob-storage](azure-blob-storage.md)
