# Import Ingest: Draft Assembly, Review Toggle and Blob Staging

### 4. Draft assembly + history grounding

Map the extracted DTO to domain entities and pre-fill fields from existing data with a tiered fuzzy match (exact → contains → token-overlap) — e.g. resolve the target parent record from the sheet's header row, suggest related rows from prior imports of the same source:

```csharp
var draft = new ImportDraft {
    Kind = kind,
    ParentId = ResolveParent(doc.Header),                // fuzzy match against existing records
    Rows = doc.Rows.Select(MapRow).ToList(),
};
```

Compute any totals/derived fields server-side.

### 5. Review toggle

`review=true` → persist immediately with a `Review` flag set (skip the client round-trip). `review=false` → return the draft **un-persisted** so the wizard can edit it; it comes back through `confirm`.

### 6. (Optional) stage the raw file in blob storage

A pipeline that must keep the source document stages the upload in a *temporary* blob container
under a `{guid}-{filename}` name **before** AI work, carries that name on the draft, and on confirm
**promotes** it to a permanent location keyed by business id. See
[`azure-blob-storage`](azure-blob-storage.md) for the passwordless `DefaultAzureCredential` pattern
and the stage→confirm lifecycle, or [`sql-stored-files`](sql-stored-files.md) to keep the bytes in
the database itself. If you only need the extracted rows, skip storage entirely.

Back to the index: [file-import-ingest](file-import-ingest.md)
