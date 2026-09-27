# MAF: extracting citation URLs from a response

## Extracting Citation URLs

Foundry agents with web-search tools annotate their responses with source URLs:

```csharp
private static IReadOnlyList<string> ExtractCitationUrls(ResponseResult response)
{
    var urls = new List<string>();

    foreach (var item in response.OutputItems)
    {
        foreach (var content in item.Content)
        {
            foreach (var annotation in content.OutputTextAnnotations)
            {
                var uri = annotation.Uri ?? annotation.Url;
                if (Uri.TryCreate(uri, UriKind.Absolute, out var parsed)
                    && (parsed.Scheme == "https" || parsed.Scheme == "http"))
                {
                    urls.Add(uri!.TrimEnd('.', ',', ';', ')'));
                }
            }
        }
    }

    return urls.Distinct(StringComparer.OrdinalIgnoreCase).ToList();
}
```

Back to the index: [dotnet-maf](dotnet-maf.md)
