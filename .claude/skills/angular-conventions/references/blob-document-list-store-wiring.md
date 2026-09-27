# Blob document list: signal store slice and loadDocuments

## Store wiring

`src/ui/src/app/store/features/with-imports.feature.ts` — the list gets its **own** loading
flag (`importDocumentsLoading`), deliberately separate from `importBusy` (the flag A1/A2
`ingestFile`/`ingestWartungsFile`/`commitDraft`/`commitWartungsDraft` use):

```typescript
export interface ImportsState {
  // ...A1/A2 draft state...
  importDocuments: ImportDocumentDto[];
  importDocumentsLoading: boolean;
  importBusy: boolean; // shared by A1/A2 ingest/commit only — NOT by loadDocuments
  // ...
}
```

```typescript
/** `GET /import/documents?houseId={guid}` — pass `undefined` for the full list.
 * Independent of the ingest/commit busy flags above so browsing retained documents
 * (e.g. on the House edit page) never disturbs an in-progress A1/A2 wizard flow. */
loadDocuments: rxMethod<string | undefined>(
  pipe(
    tap(() => patchState(store, { importDocumentsLoading: true })),
    switchMap((houseId) =>
      importService.listDocuments(houseId).pipe(
        tapResponse({
          next: (importDocuments) => patchState(store, { importDocuments }),
          error: (error: unknown) => console.error('loadDocuments error:', error),
          finalize: () => patchState(store, { importDocumentsLoading: false }),
        }),
      ),
    ),
  ),
),

/** `GET /import/documents/{id}/download` — delegates the blob/anchor-click download
 * mechanics to `ImportService` (kept out of components per project convention). */
downloadDocument(id: string, fileName: string): void {
  importService.downloadDocument(id, fileName);
},
```

Call `store.loadDocuments(houseId)` from the host page's `ngOnInit` (pass `undefined` for an
unfiltered list); call `store.downloadDocument(id, fileName)` from the row's click handler.


Back to the index: [blob-document-list](blob-document-list.md)
