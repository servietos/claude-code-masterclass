# Blob document list: the DTO and the service (list JSON + blob download)

## Reference implementation

### The DTO

`src/ui/src/app/shared/models/import.model.ts`

```typescript
/** A retained original import document. `Kind` mirrors `ImportKind` ('mieterliste' |
 * 'wartungsliste') as a plain string on the wire. `HouseId` is nullable — a Wartungsliste
 * upload can produce documents for several buildings, or none yet if nothing matched. */
export interface ImportDocumentDto {
  ID: string;
  Kind: string;
  FileName: string;
  ContentType: string;
  SizeBytes: number;
  UploadedUtc: string;
  HouseId: string | null;
}
```

### The service — list (JSON) + download (blob → anchor)

`src/ui/src/app/shared/import/import.service.ts`

```typescript
/** `GET /import/documents?houseId={guid}` — A3 Dokument-Ablage; omit `houseId` for the
 * full list. Consumed by the House edit page's "Dokumente" section. */
listDocuments(houseId?: string) {
  const url = houseId
    ? `${environment.webApiUrl}import/documents?houseId=${encodeURIComponent(houseId)}`
    : `${environment.webApiUrl}import/documents`;
  return this.http.get<ImportDocumentDto[]>(url);
}

/** `GET /import/documents/{id}/download` — fetches the retained original as a blob and
 * triggers a browser download via a transient object-URL anchor (mirrors
 * `with-tasks.feature.ts`'s `downloadTaskRunFiles`, this repo's existing blob-download
 * pattern). Blob/download handling stays in this service, never inline in a component. */
downloadDocument(id: string, fileName: string): void {
  this.http.get(`${environment.webApiUrl}import/documents/${id}/download`, { responseType: 'blob' }).subscribe((blob) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
  });
}
```

This exact `get(..., { responseType: 'blob' })` → `createObjectURL` → `<a download>` click →
`revokeObjectURL` shape is not new to A3 — it's this repo's established blob-download
precedent, first written for the Automatisierungen run-file export in
`src/ui/src/app/store/features/with-tasks.feature.ts` (`downloadTaskRunFiles`). Reuse the
shape rather than inventing a second one.


Back to the index: [blob-document-list](blob-document-list.md)
