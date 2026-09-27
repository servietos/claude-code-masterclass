# Angular Bottom Sheet (Native `<dialog>`, No CDK)

In apps with **no Angular Material and no `@angular/cdk`**, the natural modal
primitive is the native `<dialog>` element — opened imperatively with
`showModal()`/`close()` and styled via a shared `.dialog` layer. A bottom sheet
is just a variant of that same convention: instead of a centered card, the
`<dialog>` is pinned to the bottom of the viewport, full-width, and slides up on
open. Reuse the app's existing dialog styling (titlebar / close button / body);
only the outer geometry and entrance transition differ.

> **Two component shapes.** Native `<dialog>` modals in Angular tend to appear in
> one of two shapes — pick per use:
>
> 1. **Component owns its `<dialog>` internally** — exposes public
>    `open()`/`close()` methods; the host embeds `<app-x-bottom-sheet #sheet>`
>    once and drives it imperatively (`this.sheet().open()`). This is the shape
>    below — the one meant to be dropped into a host template and driven from
>    outside.
> 2. **Container drives a `<dialog #ref>` element directly** — via
>    `viewChild<ElementRef<HTMLDialogElement>>` + an `effect()` reacting to a
>    signal. Prefer this only when the dialog is tightly bound to one parent's
>    state.
>
> The bottom sheet follows shape 1.

Back to the index: [angular-bottom-sheet](angular-bottom-sheet.md)
