# Import Ingest: Confirm, Categorizer Seam and DI Wiring

### 8. Confirm / commit — insert-only, regenerate ids

```csharp
public async Task<ImportResult> ConfirmAsync(ImportDraft draft)
{
    // regenerate keys so it is always a fresh insert (EMPTY_GUID → new)
    foreach (var row in draft.Rows) { row.Id = Guid.NewGuid(); row.ParentId = draft.ParentId; }
    ctx.Rows.AddRange(draft.Rows);
    await ctx.SaveChangesAsync();
    return new ImportResult { ImportedCount = draft.Rows.Count, ParentId = draft.ParentId };
}
```

Persist through `AppDbContext` (see [`dotnet-efcore`](dotnet-efcore.md)). Decide **insert vs update** per domain: some imports *replace* a parent's rows entirely — dedup by a natural key and update-or-insert rather than blind add.

### 9. Categorize seam

Keep an `IDocumentCategorizer` returning `(Category, Confidence)` in front of the pipeline so a stub can grow into an AI/rules classifier without touching callers. Fine to ship a stub first (`Category = ..., Confidence = 1.0`), but wire the interface now.

## DI wiring (`Program.cs`)

```csharp
builder.Services.AddScoped<ImportIngestionService>();
builder.Services.AddScoped<IDocumentCategorizer, DocumentCategorizationService>();
// reuse the existing AI client registration used elsewhere in the app; add BlobStorageService only if staging files
```

Back to the index: [file-import-ingest](file-import-ingest.md)
