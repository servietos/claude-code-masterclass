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

## Vision models returning coordinates

When a vision model (Qwen-VL family on DeepInfra, e.g. `Qwen/Qwen3-VL-30B-A3B-Instruct`) must return
geometry as JSON, the same defensive stance applies, with two traps seen live:

- **Scale.** Asked for 0..1 coordinates, Qwen-VL still answers on its native 0..1000 grid in some
  replies. Ask for the 0..1000 grid outright, then normalise: if every value is at most 1.5 treat it
  as 0..1, otherwise divide by 1000.
- **Nesting.** `points` arrives flat (`[x,y,x,y]`), as pairs (`[[x,y],...]`) or one level deeper
  (`[[[x,y],[x,y]]]`). Flatten every number recursively in order, then pair them up.
- Use `response_format: {"type":"json_object"}`, still cut from the first `{` to the last `}`, drop
  unknown shape types instead of failing, and treat an empty result as "not recognised".
- A parser unit check with hand-written samples is not proof: send the exact image your renderer
  produces through the live model a few times before calling it done. Synthetic checks passed here
  while the first live round-trip failed on both traps.

## An empty reply in JSON mode: retry once

With `response_format: {"type":"json_object"}`, DeepSeek V4 Flash occasionally returns empty content,
and `JsonSerializer.Deserialize` then throws "The input does not contain any JSON tokens". A resend of
the same messages succeeds. Treat an empty or unparseable completion as retryable exactly once, and
return the provider error only when the second reply is unusable too. Do not retry a thrown HTTP
failure the same way: that is the timeout leaf's case. Verify with a test whose fake completion
returns `""` then a valid object (expect success after two calls) and `""` twice (expect the error).

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)
