# Import Ingest: Tests, Checklist and Related Leaves

## Testing (xUnit + NSubstitute + FluentAssertions — see [`dotnet-testing`](dotnet-testing.md))

- Mock the AI client (`virtual CompleteAsync`) to return a canned JSON draft — assert the extractor maps varied header sets to the same target fields.
- Assert `review=false` does NOT hit the DB; `confirm` inserts with fresh GUIDs.
- Assert dedup/update logic for re-imported source files.
- Feed a real converted sample as the extractor's input fixture.

## Checklist

- [ ] `IFormFile` buffered to `byte[]`; size + content-type validated (don't skip this).
- [ ] Content-type fork: EPPlus (xlsx) / PdfPig (text PDF) / vision model (image + scanned PDF).
- [ ] Strict JSON-schema prompt + `json_object`; case-insensitive deserialize; AI-mapped columns (not a fixed parser).
- [ ] Reuse the existing app AI client; config via a strongly-typed config class; keys resolved at runtime, not hardcoded.
- [ ] `review` toggle; draft un-persisted when false.
- [ ] Blob staging only if the source doc must be retained.
- [ ] Confirm = insert-only with regenerated ids; deliberate update-vs-insert for the domain.
- [ ] `IDocumentCategorizer` seam in place (stub OK).
- [ ] xUnit coverage with a mocked AI client and real sample fixtures.

## Related

- [`dotnet-controllers`](dotnet-controllers.md) / [`dotnet-efcore`](dotnet-efcore.md) — controller + EF patterns.
- [`dotnet-mcp-tool-design`](dotnet-mcp-tool-design.md) — expose ingest as an MCP tool so external Claude can import too.
- `angular-conventions` → [`file-import-wiz`](../../angular-conventions/references/file-import-wiz.md) / [`angular-file-dropzone`](../../angular-conventions/references/angular-file-dropzone.md) — the client half.

Back to the index: [file-import-ingest](file-import-ingest.md)
