# Blob Document List & Download

A reusable pattern for **listing server-retained files and downloading them** — built for
automation A3 (Dokument-Ablage pro Objekt), which retains every imported Mieterliste/
Wartungsliste original in blob storage and exposes a list + download endpoint. Pattern
lives in `src/ui` (maintenance-planner): `shared/import/import.service.ts`,
`store/features/with-imports.feature.ts`, and `resources/components/house-edit/`.

Hard rule, wherever you land next: **Never link an anchor straight at an authenticated API URL.**

| You want to... | Read |
| --- | --- |
| Is this the right pattern here, why must the download go through HttpClient, and what related leaves cover the neighbouring pieces? | [blob-document-list-principles](blob-document-list-principles.md) |
| How do I write listDocuments/downloadDocument and the list DTO, and what is the exact blob to object-URL to anchor sequence? | [blob-document-list-service](blob-document-list-service.md) |
| How do I render the document table with kind chip, size, date and a neutral download button, and which page should host it? | [blob-document-list-rendering](blob-document-list-rendering.md) |
| How does SourceDocument survive every draft patch untouched, and how does the wizard show the "Originaldokument abgelegt" confirmation? | [blob-document-list-source-document](blob-document-list-source-document.md) |
| How do I add the documents slice with its own loading flag so browsing never disturbs an in-progress ingest or commit? | [blob-document-list-store-wiring](blob-document-list-store-wiring.md) |
| How do I test the download URL, the mocked anchor click and revokeObjectURL, store population, and the rendered rows? | [blob-document-list-testing](blob-document-list-testing.md) |
| About to call this done: what must be true about the DTO, the service boundary, the loading flag, the button colour and the tests? | [blob-document-list-checklist](blob-document-list-checklist.md) |
