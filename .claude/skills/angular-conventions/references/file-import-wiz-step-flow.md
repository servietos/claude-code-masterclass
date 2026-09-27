# The three wizard steps: upload, review, assistant

## Step flow

`type Step = 1 | 2 | 3` — a hand-rolled rail (`@for` pills + `@if (step()===n)` bodies), **not** Angular Material stepper:

1. **Hochladen (Upload)** — `<app-file-dropzone>` + optional mobile `capture="environment"` input. While `busy()`, show an "wird analysiert…" status card.
2. **Prüfen (Review / column-mapping)** — reuse the feature's existing edit form + table bound to `draft().Rows`. The user corrects the AI's field mapping (which column → which entity field, house/product association, dates). Each edit calls `applyDraftPatch`.
3. **Assistent (optional AI refine)** — a chat panel over `{ Draft, Messages }`; the API may return a structured `PatchJson` that gets merged into the draft. Also surfaces "ähnliche" prior imports as one-click templates.

Back to the index: [file-import-wiz](file-import-wiz.md)
