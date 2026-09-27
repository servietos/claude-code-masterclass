# Azure Blob Storage (passwordless retention)

Passwordless blob retention, by reader question.

No connection strings, no `SharedKeyCredential`, no SAS tokens anywhere in this path — the only
identity primitive is `DefaultAzureCredential()`.

| You want to... | Read |
| --- | --- |
| Does this pattern fit, and what does BlobStorageService look like? one container with prefix folders, six virtual methods, the disabled exception. | [service](azure-blob-storage-service.md) |
| Registering blob storage: StorageConfig, appsettings keys, and why a blank Storage:AccountName registers a null client instead of skipping the registration. | [di-wiring](azure-blob-storage-di-wiring.md) |
| How does an uploaded file get staged, promoted only once the rows are written, recorded as ImportDocument, and downloaded back? | [retention-hook](azure-blob-storage-retention-hook.md) |
| 403 reading or writing blob data while you are subscription Owner or Contributor? read this before touching any code. | [rbac](azure-blob-storage-rbac.md) |
| How do I mock blob storage and assert the stage, promote, failure and download paths? ForPartsOf, stubbing success, the full assertion list. | [testing](azure-blob-storage-testing.md) |
| Metadata empty after listing, umlauts throwing, numbers with commas, or metadata lost on move or promote? read this. | [metadata](azure-blob-storage-metadata.md) |
| Final review pass before calling blob retention done, plus the sibling references this pattern plugs into. | [checklist](azure-blob-storage-checklist.md) |
