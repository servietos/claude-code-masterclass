# Stage on ingest, promote on confirm

## Retention hook

The pipeline this backs (`ImportIngestionService`, see `file-import-ingest.md` for the surrounding
ingest/confirm shape) stages the original upload **before** the AI/extraction work, then promotes it
**only if/when the row data itself is actually persisted**:

1. **Stage on ingest** — upload the raw bytes to `staging/{guid}-{safeFileName}`, before deciding
   whether this is a review draft or an auto-persist:

   ```csharp
   // src/my-api/Services/ImportIngestionService.cs
   private async Task<SourceDocument> StageDocumentAsync(IngestionSource source)
   {
       try
       {
           var blobName = $"{StagingPrefix}/{Guid.NewGuid()}-{SafeBlobFileName(source.FileName)}";
           await using var stream = new MemoryStream(source.Bytes);
           await blob.UploadAsync(StorageContainer, blobName, stream, source.ContentType);

           return new SourceDocument { BlobName = blobName, FileName = source.FileName, ContentType = source.ContentType, SizeBytes = source.Bytes.LongLength };
       }
       catch (Exception ex)
       {
           logger.LogEvent("ImportIngestionService-StageDocument-Error", ex);
           return null; // draft round-trips with no SourceDocument -- confirm simply skips retention
       }
   }
   ```

   The resulting `SourceDocument { BlobName, FileName, ContentType, SizeBytes }` is set on the draft
   so it round-trips through the review wizard untouched.

2. **Persist on confirm** — move `staging/...` → `{kind}/{guid}-{safeFileName}` and insert an
   `ImportDocument` row, **only** once the row upsert has actually happened:

   ```csharp
   // src/my-api/Services/ImportIngestionService.cs
   private async Task PersistSourceDocumentAsync(SourceDocument sourceDocument, string kind, Guid? parentId)
   {
       if (sourceDocument is null) return;
       try
       {
           var permanentName = $"{kind}/{Guid.NewGuid()}-{SafeBlobFileName(sourceDocument.FileName)}";
           await blob.MoveAsync(StorageContainer, sourceDocument.BlobName, permanentName, sourceDocument.ContentType);

           dc.ImportDocuments.Add(new ImportDocument { Id = Guid.NewGuid(), Kind = kind, FileName = sourceDocument.FileName, ContentType = sourceDocument.ContentType, SizeBytes = sourceDocument.SizeBytes, BlobName = permanentName, UploadedUtc = DateTime.UtcNow, ParentId = parentId });
           await dc.SaveChangesAsync();
       }
       catch (Exception ex)
       {
           logger.LogEvent("ImportIngestionService-PersistSourceDocument-Error", ex);
           // Non-fatal: the row import above already succeeded and is not rolled back --
           // retention just didn't happen this time (blob left in staging/ or move failed).
       }
   }
   ```

   Call this from **every** code path that actually writes the row data — the explicit `confirm`
   action for each `kind`, *and* the `review=true` auto-persist branch inside `ingest`. Miss the
   auto-persist branch and you leak an orphaned blob in `staging/` forever (rows imported, file
   never promoted, no `ImportDocument` row pointing at it) — wire retention to "did the data get
   written", not to "which HTTP action was called."

3. **Blob failure is never fatal to the data import.** Both helpers above wrap every blob call in
   `try/catch` and only `log + return`/`return null` — a storage outage, RBAC misconfiguration, or
   the null-client "disabled" case from the DI guard must never roll back or block the row
   upsert. This is the same non-fatal posture the file-import-ingest skill uses for AI failures.

4. **`ImportDocument` is a new, EF-migration-managed table** — it sits alongside (not instead of)
   the rest of the schema:

   ```csharp
   // src/my-api/Models/ImportDocument.cs
   public class ImportDocument
   {
       public Guid Id { get; set; }
       public string Kind { get; set; }           // e.g. "customers" | "products"
       public string FileName { get; set; }
       public string ContentType { get; set; }
       public long SizeBytes { get; set; }
       public string BlobName { get; set; }        // permanent blob name, e.g. "customers/{guid}-roster.xlsx"
       public DateTime UploadedUtc { get; set; }
       public Guid? ParentId { get; set; }          // the draft's resolved parent record, if any
   }
   ```

   Fluent config lives in an `IEntityTypeConfiguration<ImportDocument>` next to the other entity
   configurations (`entity.ToTable("ImportDocuments")`, `IsRequired()`/`HasMaxLength` on the string
   columns, indexes on `ParentId` and `Kind`) and the table is created by an EF Core migration (see
   [`dotnet-efcore`](dotnet-efcore.md)). Apply that migration against a Release build/output
   (`dotnet ef database update -c <DbContext> --configuration Release`), never against the
   `bin/Debug` output the running API holds locked. In a project that ships schema as SQL delta
   scripts rather than migrations, create the table with a delta instead (see the router's SQL delta
   row) and keep everything else in this section unchanged.

**Read/download surface** — a controller can expose `GET api/import/documents?parentId={guid?}`
(→ `List<ImportDocumentDto>`) and `GET api/import/documents/{id:guid}/download` (→
`FileStreamResult`, `Content-Disposition: attachment` via `File(content, contentType, fileName)`),
both backed by the service's `GetDocumentsAsync`/`DownloadDocumentAsync`.

Back to the index: [azure-blob-storage](azure-blob-storage.md)
