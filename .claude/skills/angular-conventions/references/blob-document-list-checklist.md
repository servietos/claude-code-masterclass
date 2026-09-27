# Blob document list: ship checklist

## Checklist

- [ ] `ImportDocumentDto`-style list DTO defined once, next to any related draft types.
- [ ] `listDocuments(entityId?)` and `downloadDocument(id, fileName)` both live in a service —
      never a component.
- [ ] Download never uses a plain `<a href="...">` at an authenticated API route — always
      `HttpClient.get(..., { responseType: 'blob' })` → `createObjectURL` → anchor `click()` →
      `revokeObjectURL`.
- [ ] The list's loading flag is its own state field, independent of any unrelated
      ingest/commit/save busy flag.
- [ ] Rendered list: filename, a kind/type chip, human-size, date, and a **black/neutral**
      download icon button — never gold (download isn't a mutation).
- [ ] Empty state text for "no documents yet", not a blank table.
- [ ] Any draft type carrying a passthrough field (like `SourceDocument`) only needs the
      field added to its TS interface — immutable `{ ...current, ...patch }` patch methods
      preserve it automatically; don't hand-thread it through every patch call site.
- [ ] Vitest at all three layers: service (URL + blob/anchor mechanics), store (population +
      "doesn't disturb unrelated state"), component (renders rows, download button fires).


Back to the index: [blob-document-list](blob-document-list.md)
