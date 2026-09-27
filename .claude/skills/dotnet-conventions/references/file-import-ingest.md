# File Import / Ingest Endpoint (ASP.NET Core)

Server side of the **file → AI-draft → review → commit** import pattern: a controller accepts an
uploaded spreadsheet/PDF, an AI call maps its columns onto domain fields, the caller reviews a
draft, and only then does the server commit rows through EF Core. The client half (drop zone +
wizard) lives in `angular-conventions` → [`angular-file-dropzone`](../../angular-conventions/references/angular-file-dropzone.md) and [`file-import-wiz`](../../angular-conventions/references/file-import-wiz.md).

**Validate** size and content-type/extension explicitly — don't skip this.

| You want to... | Read |
|---|---|
| Decide if this is the right pattern; see the four endpoints. Read first. | [file-import-ingest-overview](file-import-ingest-overview.md) |
| Write the POST: `IFormFile` buffering, `IngestionSource`, validation, `kind`. | [file-import-ingest-upload-endpoint](file-import-ingest-upload-endpoint.md) |
| Get typed fields out of an xlsx, a text PDF or a scan; pick the AI client. | [file-import-ingest-extraction](file-import-ingest-extraction.md) |
| Know what ingest returns: pre-fill, totals, review toggle, blob staging. | [file-import-ingest-draft-review](file-import-ingest-draft-review.md) |
| Chat over an un-committed draft and merge `PatchJson`. | [file-import-ingest-assist](file-import-ingest-assist.md) |
| Commit through EF Core; categorizer seam; DI wiring. | [file-import-ingest-confirm-commit](file-import-ingest-confirm-commit.md) |
| Test it, run the pre-merge checklist, find the Angular client half. | [file-import-ingest-checklist](file-import-ingest-checklist.md) |
