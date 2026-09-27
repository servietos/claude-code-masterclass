# File Import Wizard (Angular client)

Routing index for the Angular client half of the upload-to-draft-to-review-to-commit file import wizard; the server half lives in `dotnet-conventions` → [`file-import-ingest`](../../dotnet-conventions/references/file-import-ingest.md).

Key rule: **the component holds only view state; all import *data* lives in the store.**

| You want to... | Read |
|---|---|
| Check this is the right pattern, and find the server half | [overview](file-import-wiz-overview.md) |
| Know which state is a local signal and which is a store slice | [state-ownership](file-import-wiz-state-ownership.md) |
| See the three steps, and why a hand-rolled pill rail not the Material stepper | [step-flow](file-import-wiz-step-flow.md) |
| Write the wizard component: inputs, outputs, the three effects | [component](file-import-wiz-component.md) |
| Write the store slice: withState, applyDraftPatch, the rxMethods | [store-slice](file-import-wiz-store-slice.md) |
| Post the file and call ingest/assist/confirm | [service](file-import-wiz-service.md) |
| Open the wizard: toolbar button and global file drop | [entry-paths](file-import-wiz-entry-paths.md) |
| Know what breaks, and run the shipping checklist | [pitfalls](file-import-wiz-pitfalls.md) |
| Fix step 2 pickers rendering "No results" | [empty-picker](file-import-wiz-empty-picker.md) |
