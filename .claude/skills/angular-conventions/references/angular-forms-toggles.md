# Checkbox and Slide-Toggle Binding

## Boolean toggles / checkbox binding

`[formField]` binds natively to `<input type="checkbox">` via `element.checked` and the
`input`/`blur` DOM events — no custom `FormValueControl` wrapper is needed for a boolean field.

```html
<input type="checkbox" [formField]="settingsForm.enabled" />
```

```typescript
enabledModel = signal({ enabled: false });
enabledForm = form(this.enabledModel);
```

Where an app renders boolean toggles as a slide-toggle rather than a bare checkbox, the real
`<input>` stays under a shared `.toggle` component (e.g. `theme/components.scss`) — visually
hidden but focusable, with `role="switch"`:

```html
<label class="toggle">
  <input type="checkbox" role="switch" class="toggle__input" [formField]="testForm.enabled" aria-label="Testen" />
  <span class="toggle__track"></span>
  <span class="toggle__label">Testen</span>
</label>
```

**One-element variant, where the app has no shared component to hang the spans on.** Style the input
itself with `appearance: none` and draw the thumb with `::after`, so there is no track or label span
and nothing to keep in sync:

```html
<label class="switch">
  <input type="checkbox" role="switch" [formField]="detailForm.mfa" />
  MFA
</label>
```

```css
.switch input { appearance: none; position: relative; width: 2.75rem; height: 1.5rem; border-radius: var(--radius-pill); }
.switch input::after { content: ''; position: absolute; top: 50%; left: 0.15rem; width: 1.1rem; height: 1.1rem; transform: translateY(-50%); border-radius: 50%; transition: left 0.15s ease; }
.switch input:checked::after { left: calc(100% - 1.25rem); }
```

Same guarantees as the three-span version, because the input is still a real focusable checkbox:
`[formField]`, keyboard, and `role="switch"` all behave. Pick the shared component where one exists;
pick this where adding one would be the only reason to create a component. Either way the shared CSS
lives in one file (`shared/styles/toggle.css`) that component styles `@import`, never inline per screen.
Check for an existing toggle in the repo before writing a third variant.

**Dynamic-key boolean fields** — a `Record<string, boolean>` model whose keys are only known at
runtime (e.g. one boolean per dynamic table column) works the same way, because
`FieldTree<Record<string, boolean>>` structurally has an index signature:

```typescript
boolModel = signal<Record<string, boolean>>({});
boolForm = form(this.boolModel);
```

```html
<input type="checkbox" [formField]="boolForm[col.Name]" />
```


Back to the index: [angular-forms](angular-forms.md)
