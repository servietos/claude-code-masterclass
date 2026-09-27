# Prompt rules for customer-facing copy: grounding facts

## Prompt rules for customer-facing copy

This is the part most likely to go wrong quietly, because a hallucination that happens to be correct
(or plausible) passes every code review and every test. Keep all five rules below when building a
similar feature: dropping any one of them reintroduces the failure it exists to prevent.

**Ground every hard fact in the prompt, or the model will invent it.** One implementation omitted the
business's street address from the prompt and the model filled it in from general knowledge. It happened
to be correct, which is worse than an obvious error, because nothing caught it in review. Anything
concrete (an address, a price, a date, a person's name) that the model states without it being supplied
in the prompt is a hallucination regardless of whether it turns out true. Put every hard fact the model
is allowed to state directly in the system prompt:

```
Du bist die Textassistenz für <Firmenname> in <Ort> (<Strasse, PLZ Ort>).
```

Where those facts already live in the database or a settings screen, read them from there per call
rather than hardcoding them into the prompt string, so the prompt cannot drift from the business's
actual data.

**Missing facts become explicit placeholders, never invented values.** When a concrete detail is not in
the prompt data, instruct the model to emit a bracketed placeholder instead of guessing, so it is
visibly incomplete in the UI rather than silently wrong:

```
Fehlt eine konkrete Angabe (z. B. ein genauer Termin, ein Preis oder ein Name), lass an dieser Stelle
einen Platzhalter in eckigen Klammern stehen, z. B. [BITTE TERMIN EINTRAGEN] oder
[BITTE PREIS EINTRAGEN]. Erfinde niemals selbst einen plausiblen Wert.
```

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)
