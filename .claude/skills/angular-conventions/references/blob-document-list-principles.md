# Blob document list: when to use it and why this shape

## When to use

- Rendering a list of server-stored files (imports, exports, attachments, generated reports)
  against a single entity (a House, a Task run, a Reservation…).
- Any "click to download the original/generated file" button backed by an authenticated API
  route rather than a public static URL.
- You already have (or are adding) the [`file-import-wiz`](file-import-wiz.md) pipeline and
  want to surface the originals it retained.

## Core principles (why this shape)

1. **Never link an anchor straight at an authenticated API URL.** A plain
   `<a href="https://api/.../download">` performs a normal browser navigation with no
   `Authorization` header — MSAL's bearer token only rides requests made through
   `HttpClient` (intercepted by the app's auth interceptor). So the download must be a real
   `HttpClient` request; the browser-native "save this file" gesture is then faked with a
   **blob + transient object-URL anchor**, not a direct navigation.
2. **The list and the download are two independent concerns.** Listing is a `GET` returning
   JSON metadata (`ImportDocumentDto[]`); downloading is a second `GET` per file returning
   the binary as a blob. Don't conflate them into one call.
3. **Blob/anchor mechanics live in a service, never inline in a component** — this repo's
   hard rule (see `CLAUDE.md`: "keep download/blob handling in a service, never inline in
   components"). The component/store only calls `service.downloadDocument(id, fileName)`.
4. **The list has its own loading flag, independent of any "busy" flag an unrelated wizard
   flow uses.** Browsing retained documents must never disturb an in-progress import/upload
   (see `angular-signal-store-design` — one composed store, many independent slices).
5. **Download is not a create/save/delete action** — per the bico-brand two-color button
   rule, the download button is **black/neutral**, never gold.

## Related

- [`file-import-wiz`](file-import-wiz.md) — the import wizard whose drafts carry
  `SourceDocument`; this pattern is its "A3 Dokument-Ablage" companion.
- [`angular-file-dropzone`](angular-file-dropzone.md) — the upload side this pattern's
  documents originated from.
- [`angular-signal-store-design`](angular-signal-store-design.md) — why the list gets its
  own state slice/loading flag instead of reusing an unrelated one.
- [`angular-http`](angular-http.md) — `HttpClient` mutation/blob conventions, `rxMethod`.
- `bico-brand` skill — the two-color button rule (`download` is black, never gold).

Back to the index: [blob-document-list](blob-document-list.md)
