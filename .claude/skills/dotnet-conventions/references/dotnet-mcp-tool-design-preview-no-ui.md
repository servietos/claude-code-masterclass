# Preview tools for clients that cannot render a form

## Human-in-the-loop when the client has no UI

Desktop and mobile clients (Claude Desktop, iPhone, iPad) render tool results as text in a chat
bubble. They cannot show an interactive form, and you cannot rely on elicitation or sampling. A
write that deserves confirmation therefore needs a **read-only preview tool** beside the write tool,
not a UI.

Shape that works:

- `preview_x` takes the same arguments as `write_x`, writes nothing, and returns what it *would* do.
- **Array in, array out, always**, in input order, one proposal per input item. A single item is a
  one-element array, so a caller never branches on shape.
- **Essential fields only.** The reader is a human on a phone. If a field would not change their yes
  or no, leave it out. Where a value was *resolved* rather than supplied, name the rule and the
  evidence in one short field.
- An item that cannot be resolved stays in its position carrying its candidates or its error. Never
  drop it: the array length must equal the input length.
- **Stateless.** No preview token, no server-side pending store. The confirm turn may share no state
  with the preview turn; the user types "ok" and the model calls the write tool with the same
  arguments. The write tool must never require a preview to have run.
- Say in the `[Description]` that this is a dry run and the caller is expected to present it for
  confirmation.

### The write tool can be its own preview

When the server has a mode switch (a "human confirms" mode versus an "auto" mode), the cleanest shape
is not a third tool: `write_x` itself returns the proposal as **plain text** in the confirming mode
and writes nothing, ending with the question and naming the follow-up tool literally:

```text
Description: Google
Date: 2026-08-17
Net: 10.00 EUR
VAT: 20%
Gross: 12.00 EUR
Account: 7380 Telefon

Book this? Reply yes to save it, no to cancel. On yes, call save_voucher with exactly these values;
do not call add_voucher again for this booking.
```

Why text and not JSON here: the client renders a tool result verbatim in a chat bubble, so JSON is
shown to a human as JSON. One `Label: value` per line, invariant culture for money, and omit fields
that have no value rather than printing empty ones.

- **The text must carry every identifier the follow-up write tool takes, in the form it takes it.**
  Rendering an account as `7380 Telefon` reads well and is useless to a `save_voucher` that wants the
  GUID, so the model spends a turn re-listing accounts. Print the human label *and* the machine value,
  or accept the extra round trip knowingly.
- The last line is instructions to the model, not to the user, and both read it. Name the exact tool
  and forbid re-calling the proposing tool, or the model loops.
- Failures render as text too, listing the candidates one per line and asking which to use. A mode
  that returns text on success and JSON on failure makes the client show a raw error object.
- Keep the write path single: the confirming mode and the auto mode must land in the same write
  method, so defaults like "mark it paid" or "flag it as AI-booked" cannot diverge between them.

Back to the index: [dotnet-mcp-tool-design](dotnet-mcp-tool-design.md)
