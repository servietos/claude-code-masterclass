# Blob document list: the SourceDocument draft passthrough

### The `SourceDocument` pass-through (draft → wizard confirmation)

The [`file-import-wiz`](file-import-wiz.md) draft types carry an optional `SourceDocument`
set by the server on ingest — the client's job is only to **not lose it**:

`src/ui/src/app/shared/models/import.model.ts`

```typescript
/** A3 Dokument-Ablage — the original uploaded file, staged by the server into blob storage
 * on ingest and referenced from the draft it produced. Present once the server has staged
 * the file; `undefined` for older/in-flight drafts that predate A3. Both `applyDraftPatch`
 * and `applyWartungsPatch` spread the whole draft on every patch, so this rides along
 * untouched through the review step automatically — it only needs to exist on the type so
 * TS doesn't strip it. */
export interface SourceDocument {
  BlobName: string;
  FileName: string;
  ContentType: string;
  SizeBytes: number;
}

export interface ImportDraft {
  Kind: string;
  HouseId: string | null;
  Rows: HouseUnitRow[];
  SourceDocument?: SourceDocument;
}
```

Because `applyDraftPatch`/`applyWartungsPatch` always do `{ ...current, ...patch }` (see
`with-imports.feature.ts`), `SourceDocument` survives every row edit without either method
ever mentioning it by name. The wizard reads it once, right when a commit lands, to decide
whether to show the retention confirmation:

`src/ui/src/app/tasks/import-wizard/import-wizard.component.ts` (excerpt):

```typescript
// 3. when the commit result lands, show the "Import abgeschlossen" confirmation
effect(() => {
  const done = this.kind() === 'mieterliste' ? this.store.lastImportedId() : this.store.lastWartungsResult();
  if (this.accepting() && done) {
    this.accepting.set(false);
    const hadSourceDocument = !!(this.kind() === 'mieterliste' ? this.draft()?.SourceDocument : this.wartungsDraft()?.SourceDocument);
    this.sourceDocRetained.set(hadSourceDocument);
    this.committed.set(true);
    // ...
  }
});
```

```html
@if (sourceDocRetained()) {
  <p class="mt-1 text-sm text-muted">Originaldokument abgelegt ✓</p>
}
```


Back to the index: [blob-document-list](blob-document-list.md)
