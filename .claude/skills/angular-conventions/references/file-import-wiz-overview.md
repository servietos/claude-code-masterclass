# File import wizard: what it is, when to use it, where the rest lives

A standalone, multi-step **file-import wizard** — upload a document, let the API turn it into an editable draft (AI/parsing server-side), review/correct it, optionally refine it with an AI assistant, then commit. Client pattern distilled from `vouchers-ai/src/vouchers-ui` (`vouchers/voucher-booking-wiz/`) and adapted to maintenance-planner's Angular 22 + `@ngrx/signals` AppStore stack.

> The **server side** of this pattern (ingest / categorize / assist / confirm endpoints, OCR + AI draft generation, blob + EF persistence) lives in the `dotnet-conventions` skill → [`file-import-ingest`](../../dotnet-conventions/references/file-import-ingest.md). This reference is the Angular client only.

## When to use

- Building any "import a file → check what we extracted → save" flow: Mieterlisten (→ `HouseUnit`), the monthly maintenance worklist (→ `House`/`Product`/schedules), or any Excel/PDF the Hausverwaltungen send.
- The AI file-drop automations described in `docs/ai-automations/readme.md`.
- Fed by the [`angular-file-dropzone`](angular-file-dropzone.md) control on step 1.

## Related

- [`angular-file-dropzone`](angular-file-dropzone.md) — the step-1 upload control.
- [`angular-signal-store-design`](angular-signal-store-design.md) / [`angular-http`](angular-http.md) — store slice + `rxMethod`/`FormData`.
- `dotnet-conventions` → [`file-import-ingest`](../../dotnet-conventions/references/file-import-ingest.md) — the server ingest/AI/commit side.
- `docs/ai-automations/readme.md` — where these wizards plug into the app's automations.

Back to the index: [file-import-wiz](file-import-wiz.md)
