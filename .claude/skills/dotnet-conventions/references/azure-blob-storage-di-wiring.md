# DI wiring and the null-client guard

## DI wiring

`AppConfig.Storage` — read via a strongly-typed config class, never raw `IConfiguration`:

```csharp
public class StorageConfig
{
    public string AccountName { get; set; }
    public string Container { get; set; } = "import-documents";
}

public class AppConfig
{
    ...
    public StorageConfig Storage { get; set; }
}
```

`appsettings.json` / `appsettings.Development.json`:

```json
"Storage": {
  "AccountName": "mystorageaccount",
  "Container": "import-documents"
}
```

`AddBlobStorage` (`Common/AppBuilder.cs`) — the **null-client guard** so a blank
`Storage:AccountName` (e.g. before the account/RBAC is provisioned, or a stripped-down local dev
config) never crashes startup: register a `null` `BlobServiceClient` rather than skip registration
entirely, so `BlobStorageService`'s constructor (and any service that depends on it) still resolves
through DI:

```csharp
// src/my-api/Common/AppBuilder.cs
public static void AddBlobStorage(this WebApplicationBuilder builder)
{
    var cfg = builder.Configuration.Get<AppConfig>();
    var accountName = cfg?.Storage?.AccountName;

    builder.Services.AddSingleton(_ => string.IsNullOrWhiteSpace(accountName)
        ? null
        : new BlobServiceClient(new Uri($"https://{accountName}.blob.core.windows.net"), new DefaultAzureCredential()));
    builder.Services.AddScoped<BlobStorageService>();
}
```

`Program.cs` — call this **before** registering the service(s) that depend on `BlobStorageService`:

```csharp
// src/my-api/Program.cs
builder.AddBlobStorage();

builder.Services.AddScoped<IDocumentCategorizer, DocumentCategorizationService>();
builder.Services.AddScoped<ImportIngestionService>();
```

No connection strings, no `SharedKeyCredential`, no SAS tokens anywhere in this path — the only
identity primitive is `DefaultAzureCredential()`.

Back to the index: [azure-blob-storage](azure-blob-storage.md)
