# Import Ingest: The Upload Endpoint

### 1. Upload endpoint — buffer `IFormFile`, share one pipeline

```csharp
[ApiController]
[Route("import")]
public class ImportController(ImportIngestionService ingestion) : ControllerBase
{
    [HttpPost("{kind}/ingest")]
    public async Task<IngestionResult> Ingest(string kind, IFormFile file, [FromQuery] bool review)
    {
        using var stream = new MemoryStream();
        await file.CopyToAsync(stream);
        var src = new IngestionSource(stream.ToArray(), file.FileName, file.ContentType, IngestionOrigin.Upload);
        return await ingestion.IngestAsync(kind, src, review);
    }
}
```

- Receive as `IFormFile`, buffer to `byte[]` via `MemoryStream`.
- Wrap in a small record so upload and any future origin (email inbox, MCP tool) share the pipeline: `public record IngestionSource(byte[] Bytes, string FileName, string ContentType, IngestionOrigin Origin);`
- **Validate** size and content-type/extension explicitly — don't skip this. Reject anything but `.xlsx`/`.pdf`/`image/*`; cap size via `[RequestSizeLimit]` or Kestrel limits.
- `kind` selects the target mapping (e.g. `customers` → `Customer`, `products` → `Product`).

Back to the index: [file-import-ingest](file-import-ingest.md)
