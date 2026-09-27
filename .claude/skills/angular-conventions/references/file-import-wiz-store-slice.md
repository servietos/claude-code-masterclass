# withImports store feature: the ingest state machine

## Store slice (`@ngrx/signals`) — the ingest state machine

### Store slice (`@ngrx/signals`) — the ingest state machine

Add to the AppStore as its own feature (`withImports`) or fold into `withTasks`. See [`angular-signal-store-design`](angular-signal-store-design.md) and [`angular-http`](angular-http.md).

```ts
export function withImports() {
  return signalStoreFeature(
    withState({
      importDraft: null as ImportDraft | null,
      importSamples: [] as ImportSample[],
      importBusy: false,
      assistMessages: [] as AssistMessage[],
      lastImportedId: null as string | null,
    }),
    withMethods((store, svc = inject(ImportService)) => ({
      applyDraftPatch(patch: Partial<ImportDraft>) {
        const d = store.importDraft(); if (!d) return;
        patchState(store, { importDraft: { ...d, ...patch } });
      },
      clearImport() {
        patchState(store, { importDraft: null, importSamples: [], assistMessages: [], lastImportedId: null });
      },
      ingestFile: rxMethod<{ file: File; review: boolean }>(pipe(
        tap(() => patchState(store, { importBusy: true })),
        switchMap(({ file, review }) => svc.ingest(file, review).pipe(tapResponse({
          next: (r) => patchState(store, { importDraft: r.Draft, importSamples: r.Samples ?? [] }),
          error: () => { /* AILogger / toast */ },
          finalize: () => patchState(store, { importBusy: false }),
        }))),
      )),
      assist: rxMethod<{ text: string }>(pipe(
        switchMap(({ text }) => {
          const messages = [...store.assistMessages(), { Role: 'user', Content: text }];
          patchState(store, { assistMessages: messages, importBusy: true });
          return svc.assist({ Draft: store.importDraft()!, Messages: messages }).pipe(tapResponse({
            next: (r) => {
              patchState(store, { assistMessages: [...store.assistMessages(), { Role: 'assistant', Content: r.Reply }] });
              if (r.PatchJson) patchState(store, { importDraft: { ...store.importDraft()!, ...JSON.parse(r.PatchJson) } });
            },
            error: () => {},
            finalize: () => patchState(store, { importBusy: false }),
          }));
        }),
      )),
      commitDraft: rxMethod<void>(pipe(
        switchMap(() => svc.confirm(store.importDraft()!).pipe(tapResponse({
          next: (saved) => patchState(store, { lastImportedId: saved.Id /*, merge into the target list slice */ }),
          error: () => {},
        }))),
      )),
    })),
  );
}
```

Back to the index: [file-import-wiz](file-import-wiz.md)
