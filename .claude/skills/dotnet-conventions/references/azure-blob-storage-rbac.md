# The data-plane RBAC gotcha

### The RBAC gotcha worth remembering

**Subscription `Owner`/`Contributor` are control-plane roles only — `dataActions: []`.** They let you
create/list/delete the storage *account* and manage its ARM resource, but grant **zero** permission
to read/write blob *data*. `DefaultAzureCredential` calling `BlobClient.UploadAsync`/`DownloadAsync`
etc. needs an explicit **data-plane** role — `Storage Blob Data Contributor` (or `...Data Reader` for
read-only) assigned at the storage account (or container) scope, separately from any
Owner/Contributor grant. This trips people up because "I'm Owner on the subscription, why is this
403ing" is the natural first reaction — Owner/Contributor and Storage Blob Data Contributor are
orthogonal role families (control-plane ARM vs. data-plane Storage).

Provision both required assignments (the dev identity via `az login` locally, and the compute's
managed identity in the deployed environment) with `az role assignment create --role "Storage Blob
Data Contributor" --scope <storage-account-resource-id>`, guarded so it's idempotent to re-run. Every
new environment needs the identical treatment before this pattern works end-to-end there — it is not
automatic.

Back to the index: [azure-blob-storage](azure-blob-storage.md)
