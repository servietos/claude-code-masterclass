# Scope and the BlobStorageService surface

Server-side pattern for retaining an uploaded file in Azure Blob Storage with **no connection
strings or account keys** — `DefaultAzureCredential` (RBAC data-plane role) only. Built on top of
the ingest pipeline in [`file-import-ingest.md`](file-import-ingest.md).

## When to use

- A pipeline needs to **keep the original uploaded file** (not just the rows extracted from it) —
  e.g. an import service retaining the source `.xlsx`/`.pdf` against the parent record it populated.
- You want passwordless Azure Storage access (`BlobServiceClient` + `DefaultAzureCredential`) instead
  of a connection string, and a stage-then-promote (temp → permanent) blob lifecycle tied to a
  draft-review-confirm flow.
- Not for arbitrary blob CRUD outside this "stage on ingest, promote on confirm" shape — for that,
  use `Azure.Storage.Blobs` directly rather than bending this skill's `BlobStorageService`.

## The pattern

**One container, prefix folders — not one container per kind.** Use exactly one container
(`AppConfig.Storage.Container`) and use blob-name **prefixes** as the "folder per import type":
`staging/` (uploaded, not yet confirmed) → `{kind}/` (confirmed, permanent). `BlobStorageService.MoveAsync`
takes **one** container plus a source/destination name within it:

```csharp
// src/my-api/Services/BlobStorageService.cs
public virtual async Task MoveAsync(string container, string srcName, string dstName, string contentType)
{
    if (!IsEnabled) throw new BlobStorageDisabledException();
    var (content, ct) = await DownloadAsync(container, srcName);
    using var ms = new MemoryStream();
    await content.CopyToAsync(ms);
    ms.Position = 0;
    await UploadAsync(container, dstName, ms, ct ?? contentType);
    await DeleteAsync(container, srcName);
}
```

Move is still download+reupload+delete (not a server-side rename/copy) — the SDK/passwordless RBAC
setup doesn't guarantee an atomic rename primitive.

**Six methods, all `virtual`, all guarded by an `IsEnabled` check:**

```csharp
// src/my-api/Services/BlobStorageService.cs
public class BlobStorageService(BlobServiceClient client)
{
    // The DI registration (see below) provides a null BlobServiceClient when
    // Storage:AccountName is blank (e.g. local dev without Azure) so the app still boots;
    // every method below no-ops/throws predictably instead of NullReferenceException, and
    // callers that wrap this service stay non-fatal too.
    private bool IsEnabled => client != null;

    public virtual async Task EnsureContainerAsync(string container) { ... }   // no-op when disabled
    public virtual async Task UploadAsync(string container, string name, Stream content, string contentType) { ... } // throws when disabled
    public virtual async Task<bool> ExistsAsync(string container, string name) { ... }  // false when disabled
    public virtual async Task<(Stream Content, string ContentType)> DownloadAsync(string container, string name) { ... } // throws when disabled
    public virtual async Task DeleteAsync(string container, string name) { ... }  // no-op when disabled
    public virtual async Task MoveAsync(string container, string srcName, string dstName, string contentType) { ... } // throws when disabled
}
```

`virtual` on every method exists for exactly one reason: `Substitute.ForPartsOf<BlobStorageService>`
in tests (see [Testing](#testing) below) — same reason the AI chat client's `CompleteAsync` is
`virtual` in `file-import-ingest.md`.

`BlobStorageDisabledException` is a small dedicated exception (not a generic one) so the "storage
isn't configured" case reads clearly in logs, distinct from a genuine Azure outage:

```csharp
// src/my-api/Services/BlobStorageService.cs
public class BlobStorageDisabledException() : System.Exception("Blob storage is not configured (Storage:AccountName is blank).");
```

Back to the index: [azure-blob-storage](azure-blob-storage.md)
