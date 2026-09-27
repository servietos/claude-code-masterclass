# Serving the A2UI Component Catalog

## Serving the Catalog

The client renderer needs the catalog to know which components exist. Serve the same catalog file the system prompt embeds so agent and client always stay in sync.

Embed the catalog JSON Schema in the assembly:

```xml
<!-- .csproj -->
<ItemGroup>
  <EmbeddedResource Include="A2Ui/catalog.json" />
</ItemGroup>
```

Singleton catalog loader:

```csharp
public class A2UiCatalogService
{
    private readonly byte[] _bytes;

    public A2UiCatalogService()
    {
        var asm = typeof(A2UiCatalogService).Assembly;
        using var stream = asm.GetManifestResourceStream("MyApp.A2Ui.catalog.json")
            ?? throw new InvalidOperationException("Embedded resource 'A2Ui/catalog.json' not found.");
        using var ms = new MemoryStream();
        stream.CopyTo(ms);
        _bytes = ms.ToArray();
    }

    public Stream OpenStream() => new MemoryStream(_bytes, writable: false);
    public string Json => System.Text.Encoding.UTF8.GetString(_bytes);
}
```

Controller:

```csharp
[ApiController]
[Route("api/a2ui/catalog")]
public class A2UiCatalogController(A2UiCatalogService catalog) : ControllerBase
{
    [HttpGet]
    [Produces("application/json")]
    public IActionResult Get() => File(catalog.OpenStream(), "application/json");
}
```

To proxy the upstream basic catalog at `https://a2ui.org/specification/v0_9/basic_catalog.json` instead, fetch it once at startup with a hosted service and cache it in memory. The hosted-service pattern avoids embedding a file and always tracks the upstream version, at the cost of an outbound request.

Back to the index: [dotnet-a2ui-endpoint](dotnet-a2ui-endpoint.md)
