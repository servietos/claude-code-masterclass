# File Drop Zone: Host Wiring to AppStore

## Host wiring (AppStore, this repo)

The host feature owns the store call. Files flow into the matching `@ngrx/signals` slice — e.g. an import automation in `withTasks`/a new `withImports` feature:

```ts
@Component({ /* … */ imports: [FileDropzone] })
export class SomeAutomationPanel {
  private store = inject(AppStore);

  onFilesSelected(files: File[]) {
    const file = files[0];
    if (!file) return;
    this.store.ingestFile({ file, kind: 'mieterliste' });   // rxMethod on the store — see angular-http / with-tasks
  }
}
```

```html
<app-file-dropzone
  label="Mieterliste (Excel oder PDF)"
  accept=".xlsx,.pdf,application/pdf"
  [busy]="store.isBusy()"
  (filesSelected)="onFilesSelected($event)" />
```

Back to the index: [angular-file-dropzone](angular-file-dropzone.md)
