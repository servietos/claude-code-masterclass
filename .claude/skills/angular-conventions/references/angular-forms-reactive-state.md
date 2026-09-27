# Reactive Form State and Events

## Form State Management

### State Properties

```typescript
// Check states
form.valid      // All validations pass
form.invalid    // Has validation errors
form.pending    // Async validation in progress
form.dirty      // Value changed by user
form.pristine   // Value not changed
form.touched    // Control has been focused
form.untouched  // Control never focused

// Update values
form.setValue({ name: 'John', email: 'john@example.com' }); // Must include all
form.patchValue({ name: 'John' }); // Partial update

// Reset
form.reset();
form.reset({ name: 'Default' });

// Disable/Enable
form.disable();
form.enable();
form.controls.email.disable();

// Mark states
form.markAllAsTouched(); // Show all errors
form.markAsPristine();
form.markAsDirty();
```

### Value Changes Observable

```typescript
// Subscribe to value changes
form.valueChanges.subscribe(value => {
  console.log('Form value:', value);
});

// Single control with debounce
form.controls.email.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged()
).subscribe(email => {
  this.validateEmail(email);
});

// Status changes
form.statusChanges.subscribe(status => {
  console.log('Form status:', status); // VALID, INVALID, PENDING
});
```

### Unified Events (Angular v22+)

```typescript
import { 
  ValueChangeEvent, StatusChangeEvent, 
  FormSubmittedEvent, FormResetEvent 
} from '@angular/forms';

form.events.subscribe(event => {
  if (event instanceof ValueChangeEvent) {
    console.log('Value changed:', event.value);
  }
  if (event instanceof StatusChangeEvent) {
    console.log('Status changed:', event.status);
  }
  if (event instanceof FormSubmittedEvent) {
    console.log('Form submitted');
  }
  if (event instanceof FormResetEvent) {
    console.log('Form reset');
  }
});
```


Back to the index: [angular-forms](angular-forms.md)
