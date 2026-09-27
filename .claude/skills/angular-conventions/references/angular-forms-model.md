# Signal Form Models

## Form Models

Form models are writable signals that serve as the single source of truth:

```typescript
// Define interface for type safety
interface UserProfile {
  name: string;
  email: string;
  age: number | null;
  preferences: {
    newsletter: boolean;
    theme: 'light' | 'dark';
  };
}

// Create model signal with initial values
const userModel = signal<UserProfile>({
  name: '',
  email: '',
  age: null,
  preferences: {
    newsletter: false,
    theme: 'light',
  },
});

// Create form from model
const userForm = form(userModel);

// Access nested fields via dot notation
userForm.name                    // FieldTree<string>
userForm.preferences.theme       // FieldTree<'light' | 'dark'>
```

### Reading Values

```typescript
// Read entire model
const data = this.userModel();

// Read field value via field state
const name = this.userForm.name().value();
const theme = this.userForm.preferences.theme().value();
```

### Updating Values

```typescript
// Replace entire model
this.userModel.set({
  name: 'Alice',
  email: 'alice@example.com',
  age: 30,
  preferences: { newsletter: true, theme: 'dark' },
});

// Update single field
this.userForm.name().value.set('Bob');
this.userForm.age().value.update(age => (age ?? 0) + 1);
```


Back to the index: [angular-forms](angular-forms.md)
