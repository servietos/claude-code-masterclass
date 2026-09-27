# The three CSS traps Tailwind's reset and layers set

## Traps, in the order they bite

### The `*` reset deletes every Tailwind border

Legacy Angular apps commonly ship

```scss
* { margin: 0; padding: 0; border: 0; font-size: 100%; }
```

That `border: 0` is unlayered, so it silently overrides `border`, `border-b` and every other border
utility. No error, no warning, just no borders anywhere. Delete the rule; preflight already resets
margins and box-sizing properly. Keep at most `body { margin: 0 }`.

### `@apply` takes utilities only

`@apply btn` inside `.btn-primary` fails with *"Cannot apply unknown utility class"*, and so does
`@apply no-scrollbar` when `no-scrollbar` lives in `@layer components`. Two fixes:

- compose in the template: `class="btn btn-primary"`
- or declare the helper as a real utility so it becomes `@apply`-able:

```css
@utility no-scrollbar {
  scrollbar-width: none;
  -ms-overflow-style: none;
  &::-webkit-scrollbar { width: 0; height: 0; display: none; }
}
```

`peer` is a marker class, not a utility: put it directly on the element. Variants built on it
(`peer-checked:bg-primary`) do work through `@apply`.

### Preflight zeroes `<dialog>` margins

`showModal()` centres a dialog through the UA stylesheet's `margin: auto`. Preflight removes it and
the modal renders flush top-left. Set `margin: auto` explicitly:

```css
.modal {
  @apply w-[min(92vw,32rem)] rounded-lg border-0 bg-transparent p-0;
  margin: auto;
  max-height: calc(100dvh - 2rem);
}
.modal::backdrop { background-color: rgb(15 34 46 / 0.45); }
```

Native `<dialog>` stays the right replacement for `MatDialog`: focus trap, Esc, inert background and
`::backdrop` come free. Wire it with `viewChild.required` + `afterRenderEffect(() => el.showModal())`,
and handle `(close)` and `(cancel)` so Esc routes the same way as the Cancel button.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)
