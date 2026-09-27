# Field State and Error Display

## Field State

Each field provides reactive signals for validation, interaction, and availability:

```typescript
const emailField = this.form.email();

// Validation state
emailField.valid()      // true if passes all validation
emailField.invalid()    // true if has validation errors
emailField.errors()     // array of error objects
emailField.pending()    // true if async validation in progress

// Interaction state
emailField.touched()    // true after focus + blur — ONLY for [formField]-bound controls
emailField.dirty()      // true after user modification

// Availability state
emailField.disabled()   // true if field is disabled
emailField.hidden()     // true if field should be hidden
emailField.readonly()   // true if field is readonly

// Value
emailField.value()      // current field value (signal)
```

### Form-Level State

The form itself is also a field with aggregated state:

```typescript
// Form is valid when all interactive fields are valid
this.form().valid()

// Form is touched when any field is touched
this.form().touched()

// Form is dirty when any field is modified
this.form().dirty()
```

## Displaying Errors

```html
<input [formField]="form.email" />

@if (form.email().touched() && form.email().invalid()) {
  <ul class="errors">
    @for (error of form.email().errors(); track error) {
      <li>{{ error.message }}</li>
    }
  </ul>
}

@if (form.email().pending()) {
  <span>Validating...</span>
}
```

## Styling Based on State

```html
<input
  [formField]="form.email"
  [class.is-invalid]="form.email().touched() && form.email().invalid()"
  [class.is-valid]="form.email().touched() && form.email().valid()"
/>
```


Back to the index: [angular-forms](angular-forms.md)
