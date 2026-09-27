# Angular Form Patterns

Reactive forms in Angular: building and typing them, repeating rows, validators, state and events, and the template-side error and submit patterns.

For production applications requiring stability guarantees, use Reactive Forms.

| You want to... | Read |
| --- | --- |
| Build a reactive form with FormBuilder, and nest a FormGroup (address block) inside it | [angular-form-patterns-reactive-basics](angular-form-patterns-reactive-basics.md) |
| Understand why a control is typed `FormControl<string \| null>`, and get nonNullable controls or a typed FormGroup interface | [angular-form-patterns-typed-forms](angular-form-patterns-typed-forms.md) |
| Render a repeating list of form rows the user can add to and remove from | [angular-form-patterns-form-array](angular-form-patterns-form-array.md) |
| Write a ValidatorFn, validate one field against another (password match), or validate against the server | [angular-form-patterns-custom-validators](angular-form-patterns-custom-validators.md) |
| Know which state flag to check (dirty, touched, pending), and subscribe to value, status or the v21+ unified events | [angular-form-patterns-state-and-events](angular-form-patterns-state-and-events.md) |
| Fix validation errors that do not show, or a submit button that stays enabled while submitting | [angular-form-patterns-errors-and-submit](angular-form-patterns-errors-and-submit.md) |
