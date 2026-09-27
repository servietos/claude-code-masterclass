# Import Ingest: When to Use It and the Endpoint Shape

## When to use

- A controller must accept an uploaded Excel/PDF and turn it into editable domain rows (e.g. an
  uploaded roster spreadsheet → `Customer`/`Product` rows) — column headers vary per source file, so
  a fixed parser breaks on every new source.
- You want the AI/parsing to live in ONE place (the server) so the client only ships `FormData` and
  renders/commits a draft.

## The shape (9 pieces)

```
POST /import/{kind}/ingest  (IFormFile, ?review=bool)   → extract → AI draft → return draft (un-persisted)
POST /import/assist         ({ Draft, Messages })        → chat over draft → { Reply, PatchJson, Refs }
POST /import/{kind}/confirm ({ reviewed draft })         → regenerate ids → EF insert
POST /documents/categorize  (IFormFile)                  → { Category, Confidence }  (seam, may start as a stub)
```

Back to the index: [file-import-ingest](file-import-ingest.md)
