# Opening the wizard: explicit button and global file drop

## Two entry paths (mirror them)

1. **Explicit** — a toolbar "Importieren" button sets `importVisible.set(true)`; template renders `@if (importVisible()) { <app-import-wizard (closed)="onClosed()" /> }`; the user uploads inside step 1.
2. **Global drop** — a shared drop target fires a store file-drop event; a host `effect()` calls the API to categorize the file, sets `pendingImportFile` + `importVisible`; the wizard's `initialFile` effect auto-ingests and jumps straight to review (step 2). See the store-event variant in [`angular-file-dropzone`](angular-file-dropzone.md).

Back to the index: [file-import-wiz](file-import-wiz.md)
