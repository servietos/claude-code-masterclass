# Blob document list: rendering the rows and where the section lives

### Rendering — list rows with a kind chip, size, date, and a neutral download button

`src/ui/src/app/resources/components/house-edit/house-edit.component.html` (excerpt):

```html
@if (isEditMode()) {
  <section class="form-section">
    <div class="section-bar">Dokumente</div>

    @if (importDocumentsLoading()) {
      <p class="py-2 text-sm text-muted" aria-live="polite">Lade Dokumente…</p>
    } @else {
      <table class="data-table w-full">
        <thead>
          <tr>
            <th>Datei</th>
            <th>Art</th>
            <th class="text-right">Größe</th>
            <th>Hochgeladen</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @for (doc of importDocuments(); track doc.ID) {
            <tr>
              <td>{{ doc.FileName }}</td>
              <td><span class="chip">{{ documentKindLabel(doc.Kind) }}</span></td>
              <td class="text-right tabular-nums">{{ formatFileSize(doc.SizeBytes) }}</td>
              <td>{{ formatDocumentDate(doc.UploadedUtc) }}</td>
              <td class="text-right">
                <button
                  type="button"
                  class="rounded p-1 hover:bg-surface-alt"
                  aria-label="Herunterladen"
                  uxTooltip="Herunterladen"
                  (click)="downloadDocument(doc)"
                >
                  <span class="material-icons text-base" aria-hidden="true">download</span>
                </button>
              </td>
            </tr>
          } @empty {
            <tr><td colspan="5" class="py-4 text-center text-muted">Keine abgelegten Dokumente für dieses Objekt.</td></tr>
          }
        </tbody>
      </table>
    }
  </section>
}
```

Note the download button is a plain neutral icon button (`hover:bg-surface-alt`, no
`ux-button variant="gold"`) — downloading doesn't create, save, or delete anything, so it
never gets the gold treatment (see `bico-brand` → "Buttons — TWO colors, chosen by action").

`src/ui/src/app/resources/components/house-edit/house-edit.component.ts` (excerpt):

```typescript
protected readonly importDocuments = this.store.importDocuments;
protected readonly importDocumentsLoading = this.store.importDocumentsLoading;

ngOnInit(): void {
  const id = this.id();
  if (!id) return;
  // ...pre-populate the edit form from the store...
  this.store.loadDocuments(id);
}

protected downloadDocument(doc: ImportDocumentDto): void {
  this.store.downloadDocument(doc.ID, doc.FileName);
}
```

### Where it lives

The House edit page (`resources/components/house-edit`), **edit-mode only** (`isEditMode()`
gates the whole section — a not-yet-saved "new" House has no `id` to query documents for).
This was the natural fit here because the House edit component already had the `id` input,
the `AppStore` injection, and an `ngOnInit` to hook into — no new route or shell needed. If
your target entity doesn't have an existing detail/edit page to host it, a compact list on
whatever page originates the imports (e.g. an automations/tasks page) is the fallback.


Back to the index: [blob-document-list](blob-document-list.md)
