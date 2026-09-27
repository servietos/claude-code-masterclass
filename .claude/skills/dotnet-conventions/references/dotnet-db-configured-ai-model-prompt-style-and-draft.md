# Prompt rules for customer-facing copy: house style and the operator's draft

Rules 3 and 4 of the five prompt rules for customer-facing copy.

**Encode house style in the system prompt, because no human reviews every generation.** The operator
reads the draft and may send it with light edits or none at all, so style rules that live only in a
style guide never reach the output. One implementation's first generation shipped en dashes despite a
standing house rule against them, so the fix was to spell the rule out explicitly, including the literal
characters to avoid:

```
Immer Deutsch, immer in der informellen Du-Form. Kein Markdown (keine Sternchen, keine Listen mit
Bindestrichen), keine Emojis. Keine Gedankenstriche als Satzzeichen (weder - noch – noch —). Nutze
stattdessen Komma, Doppelpunkt, Strichpunkt oder Klammern.
```

**Feed the full conversation and the human's in-progress draft, and instruct the model to build on the
draft, not replace it.** The user prompt carries the inbound message, every prior reply in chronological
order, and whatever the operator has already typed in the textarea. The system prompt makes the priority
explicit: an existing draft's facts and intent win over anything the model would otherwise produce:

```
Wird im Nutzer-Prompt ein "Aktueller Entwurf" mitgegeben und ist dieser nicht leer, baue direkt darauf
auf: übernimm Absicht, alle genannten Fakten sowie alle konkreten Termine oder Preise aus dem Entwurf
unverändert und formuliere daraus eine vollständige, gut geschriebene Antwort. Verwirf den Entwurf
niemals.
```

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)
