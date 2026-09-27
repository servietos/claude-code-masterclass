# Model an on/off enrichment as an additive instruction, not an enum member

Rule 5 of the five prompt rules for customer-facing copy.

**Model an on/off enrichment as an additive instruction layered on the chosen intent, not as another
enum member.** A flag such as "also include the offering and pricing" belongs on the request as a
`bool`, not as an extra member of the intent enum, because it composes with any of the real intents
(confirm, propose an alternative, decline) rather than replacing one:

```csharp
// An additive toggle, not another intent: it can be layered onto any of the actions above
// (for example "decline, and send the pricing information anyway").
private static string DescribeIncludeInfo(bool includeInfo) => includeInfo
    ? "Baue zusätzlich einen kurzen, natürlich in den Text eingewobenen Abschnitt zu Angebot, ..."
    : "Erwähne Angebot, Zeiten oder Preise in dieser Antwort nicht von dir aus.";
```

Had that flag been a fourth intent value, "decline and also send pricing" would need its own enum
member, and every future combination would double the enum. A `bool` (or a short list of independent
booleans) that the prompt-builder composes onto whichever intent was chosen keeps the combinations
linear instead of multiplicative. The same trap appears in the UI: controls that look alike in a
mockup are not necessarily the same kind of thing, and one that changes the meaning of the others is a
flag, not another action.

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)
