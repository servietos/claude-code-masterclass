# Blob retention checklist

## Checklist

- [ ] One shared container (`AppConfig.Storage.Container`) with prefix folders per stage/kind — not
      a new container per kind.
- [ ] Retained blobs carry the parent row's identity as metadata, encoded for ASCII, with numbers
      invariant, and every move/promote carries it across.
- [ ] Listing requests `BlobTraits.Metadata`, and a test asserts a non-empty map from `ListAsync`.
- [ ] `BlobStorageService` methods are all `virtual`; constructor takes `BlobServiceClient` only (no
      connection string/key parameter anywhere).
- [ ] `AddBlobStorage` registers a **null** `BlobServiceClient` (not a skipped registration) when
      `Storage:AccountName` is blank, so DI still resolves and the app boots.
- [ ] `AppConfig.Storage` bound and read through a strongly-typed config class — never `IConfiguration` directly.
- [ ] Stage on ingest, persist (move + insert) on confirm **and** on any auto-persist path that
      writes the same row data — not just the literal "confirm" action.
- [ ] Every blob call from the ingestion service is wrapped in try/catch; a storage failure never
      blocks or rolls back the row import.
- [ ] New retained-document entity is EF-migration-managed, not bolted onto an existing table by hand.
- [ ] Data-plane RBAC (`Storage Blob Data Contributor`) is assigned separately from any
      Owner/Contributor control-plane role, for both the local dev identity and the target
      compute's managed identity.
- [ ] Tests mock `BlobStorageService` via `Substitute.ForPartsOf` and explicitly stub success on
      happy-path tests (unstubbed calls hit the real "disabled" guard).

## Related

- [`file-import-ingest`](file-import-ingest.md) — the ingest/draft/review/confirm pipeline this
  retention hook plugs into (`ImportIngestionService`, `ImportController`).
- [`dotnet-efcore`](dotnet-efcore.md) — EF Core model/migration conventions (`ImportDocument` follows
  the same migration-managed pattern as any other new table).
- [`dotnet-testing`](dotnet-testing.md) — xUnit/FluentAssertions/NSubstitute conventions.
Back to the index: [azure-blob-storage](azure-blob-storage.md)
