# Submitting and Resetting

## Form Submission

```typescript
import { submit } from '@angular/forms/signals';

@Component({
  template: `
    <form (submit)="onSubmit($event)">
      <input [formField]="form.email" />
      <input [formField]="form.password" />
      <button type="submit" [disabled]="form().invalid()">Submit</button>
    </form>
  `,
})
export class Login {
  model = signal({ email: '', password: '' });
  form = form(this.model, (schemaPath) => {
    required(schemaPath.email);
    required(schemaPath.password);
  });
  
  onSubmit(event: Event) {
    event.preventDefault();
    
    // submit() marks all fields touched and runs callback if valid
    submit(this.form, async () => {
      await this.authService.login(this.model());
    });
  }
}
```

## Reset Form

```typescript
async onSubmit() {
  if (!this.form().valid()) return;
  
  await this.api.submit(this.model());
  
  // Clear interaction state
  this.form().reset();
  
  // Clear values
  this.model.set({ email: '', password: '' });
}
```


Back to the index: [angular-forms](angular-forms.md)
