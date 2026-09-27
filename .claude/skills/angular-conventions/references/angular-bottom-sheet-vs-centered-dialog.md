# Bottom sheet or centered .dialog

## When to use a bottom sheet vs. a centered `.dialog`

| Use `.dialog` (centered) when… | Use a bottom sheet when… |
| --- | --- |
| The content is a form or needs the user's full attention (confirmations, edit forms) | The content is a short list of actions or a compact status/detail panel (a quick-actions menu, a mobile-friendly detail card) |
| Desktop-first content, comfortable at any viewport width | Content reads naturally full-width and anchored to a thumb-reachable zone on mobile/tablet |
| The interaction should feel modal and centered | The interaction should feel like a drawer sliding up from the device edge |

Both variants are native `<dialog>` under the hood — same `showModal()` /
`close()` mechanics, same `::backdrop` scrim, same focus-trap behavior. Only
the geometry and entrance transition differ.

Back to the index: [angular-bottom-sheet](angular-bottom-sheet.md)
