# Reactive Error and Submit Patterns

## Error Display Pattern

```typescript
@Component({
  template: `
    <input formControlName="email" />
    
    @if (form.controls.email.invalid && form.controls.email.touched) {
      <div class="errors">
        @if (form.controls.email.errors?.['required']) {
          <span>Email is required</span>
        }
        @if (form.controls.email.errors?.['email']) {
          <span>Invalid email format</span>
        }
      </div>
    }
  `,
})
export class Form {
  // Helper for cleaner templates
  hasError(controlName: string, errorKey: string): boolean {
    const control = this.form.get(controlName);
    return control?.hasError(errorKey) && control?.touched || false;
  }
}
```

## Form Submission Pattern

```typescript
@Component({
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <!-- fields -->
      <button type="submit" [disabled]="form.invalid || isSubmitting">
        {{ isSubmitting ? 'Submitting...' : 'Submit' }}
      </button>
    </form>
  `,
})
export class Form {
  isSubmitting = false;
  
  async onSubmit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    
    this.isSubmitting = true;
    try {
      await this.api.submit(this.form.getRawValue());
      this.form.reset();
    } catch (error) {
      // Handle error
    } finally {
      this.isSubmitting = false;
    }
  }
}
```

Back to the index: [angular-forms](angular-forms.md)
