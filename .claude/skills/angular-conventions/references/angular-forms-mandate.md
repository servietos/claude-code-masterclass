# Signal Forms Are the Standard

Build type-safe, reactive forms using Angular's Signal Forms API. Signal Forms provide automatic two-way binding, schema-based validation, and reactive field state.

Signal Forms (`form()` + `[formField]` from `@angular/forms/signals`) are the mandated standard for Angular 22+ signal-based applications, used for every input including single-field ones like a year dropdown. Do not replace `form()`/`FormField` with plain `linkedSignal` + native `[value]`/`(change)` bindings, and do not switch such an app back to Reactive Forms. Specs or optimization docs that recommend "replace `form()` with a plain signal for simple selects" should be pushed back on, not applied. Removing `FormField` imports or rewriting to native bindings breaks pattern consistency and will be rejected. When in doubt, keep Signal Forms. Reactive Forms patterns at the bottom of this file are retained only for maintenance of legacy codebases and for complex, dynamic forms in existing codebases.

**Stability caveat.** Signal Forms are recommended for new signal-based applications and are shipped and fully functional as of Angular **22** — `@angular/forms/signals` is present and works, and the 21 → 22 upgrade brought no Signal Forms API delta (`form()`, `FormField`, `required()`, `email()`, `disabled()`, `hidden()` are unchanged). But **every exported symbol is still `@experimental` in 22**. Signal Forms is the standard for signal-based apps, but re-verify the API surface whenever `@angular/core`/`@angular/forms` are upgraded, since experimental signatures can change.

Back to the index: [angular-forms](angular-forms.md)
