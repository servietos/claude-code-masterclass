# Import Ingest: Assist, Chat Over a Draft

### 7. Assist (chat-over-draft)

```csharp
[HttpPost("assist")]
public async Task<AssistResult> Assist([FromBody] AssistRequest req)
{
    var messages = new List<AiChatMessage> {
        new() { Role = "system", Content = """
            You help correct an imported draft. When you suggest concrete changes,
            return them in PatchJson as a JSON object of draft fields to merge; else null.
            Return ONLY: { "Reply": "string", "PatchJson": "json string or null", "ReferenceIds": [] }
            """ },
        new() { Role = "user", Content = $"Draft:\n{JsonSerializer.Serialize(req.Draft)}" },
    };
    messages.AddRange((req.Messages ?? []).Select(m => new AiChatMessage { Role = m.Role, Content = m.Content }));
    var json = await ai.CompleteAsync(messages, json: true);
    return JsonSerializer.Deserialize<AssistResult>(json, CaseInsensitive)!;
}
```

`PatchJson` is deliberately a **string** holding a partial JSON object the client merges into the draft — the model returns `null` when it has no concrete change.

Back to the index: [file-import-ingest](file-import-ingest.md)
