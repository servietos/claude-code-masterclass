# Signal Form Fields

## Form State with Signals

```typescript
interface FormState<T> {
  value: T;
  touched: boolean;
  dirty: boolean;
  valid: boolean;
  errors: string[];
}

function createFormField<T>(
  initialValue: T,
  validators: ((value: T) => string | null)[] = []
) {
  const value = signal(initialValue);
  const touched = signal(false);
  const dirty = signal(false);
  
  const errors = computed(() => {
    return validators
      .map(v => v(value()))
      .filter((e): e is string => e !== null);
  });
  
  const valid = computed(() => errors().length === 0);
  
  return {
    value,
    touched: touched.asReadonly(),
    dirty: dirty.asReadonly(),
    errors,
    valid,
    
    setValue(newValue: T) {
      value.set(newValue);
      dirty.set(true);
    },
    
    markTouched() {
      touched.set(true);
    },
    
    reset() {
      value.set(initialValue);
      touched.set(false);
      dirty.set(false);
    },
  };
}

// Usage
@Component({...})
export class Signup {
  email = createFormField('', [
    v => !v ? 'Email is required' : null,
    v => !v.includes('@') ? 'Invalid email' : null,
  ]);
  
  password = createFormField('', [
    v => !v ? 'Password is required' : null,
    v => v.length < 8 ? 'Password must be at least 8 characters' : null,
  ]);
  
  formValid = computed(() => 
    this.email.valid() && this.password.valid()
  );
}
```

Back to the index: [angular-signals](angular-signals.md)
