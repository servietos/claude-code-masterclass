# touched() Never Flips on a Custom Control

The error branch referred to below is the one shown in [angular-forms-conditional](angular-forms-conditional.md).

#### A custom control gets none of that wiring

`touched()` flips on blur because `[formField]` installs the listener. A custom component that
wraps its own `<input>` (an autocomplete, a combobox, a currency field) is not `[formField]`-bound,
so blur is invisible to the form and `touched()` stays `false` forever — the error branch above can
never render, while a plain `[formField]` control sitting next to it behaves correctly. That
contrast is the diagnostic: if validation works on some fields in a form and not others, compare
how each is bound before looking at the validators.

The component emits blur; the parent marks the field:

```typescript
// custom control
readonly inputBlur = output<void>();
protected onBlur() { this.inputBlur.emit(); }
```

```html
<app-autocomplete [value]="model().Text" (valueChange)="onTextChange($event)" (inputBlur)="onTextBlur()" />
```

```typescript
// parent
protected onTextBlur() { this.headerForm.Text().markAsTouched(); }
```

Two failure modes, and one symptom covers both: the handler exists but never calls
`markAsTouched()`, or the `(inputBlur)` binding is missing from the template so blur is dropped
silently. Both fields in one form failed this way for different reasons — check each binding
individually rather than fixing the first and assuming the second matches.


Back to the index: [angular-forms](angular-forms.md)
