# Deterministic parsing with a defensive fallback

## Deterministic parsing with a defensive fallback

Ask the model for a fixed two-part shape in the system prompt, and never trust it fully at parse time:

```
Betreff: <hier der Betreff>
---
<hier der vollständige Antworttext mit Zeilenumbrüchen>
```

Parse it defensively: strip markdown code fences first (some providers wrap output in ` ``` ` even
when told not to), then look for the subject prefix and the `---` separator, falling back to the
caller's own subject and treating the whole text as the body when the model does not comply:

```csharp
internal static (string Subject, string Body) ParseResponse(string raw, string fallbackSubject)
{
    var text = StripCodeFences(raw).Trim();
    var lines = text.Replace("\r\n", "\n").Split('\n');

    string? subject = null;
    var bodyStartIndex = 0;

    if (lines.Length > 0 && lines[0].StartsWith("Betreff:", StringComparison.OrdinalIgnoreCase))
    {
        subject = lines[0]["Betreff:".Length..].Trim();
        bodyStartIndex = 1;
        if (lines.Length > 1 && lines[1].Trim() == "---")
            bodyStartIndex = 2;
    }

    var body = string.Join("\n", lines.Skip(bodyStartIndex)).Trim();

    if (string.IsNullOrWhiteSpace(subject))
        subject = string.IsNullOrWhiteSpace(fallbackSubject) ? DefaultSubject : fallbackSubject;
    if (string.IsNullOrWhiteSpace(body))
        body = text;

    return (subject, body);
}
```

Finally, truncate to the DTO's hard limit: the client renders this into a fixed-size textarea, and a
provider that ignores `max_tokens` must not blow past what the UI can hold.

```csharp
private const int MaxBodyLength = 4000;

internal static string TruncateBody(string body) =>
    body.Length <= MaxBodyLength ? body : body[..MaxBodyLength];
```

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)
