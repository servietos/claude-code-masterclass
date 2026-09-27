# Component anatomy and CLI scaffolding

Create standalone components for Angular v20+. Components are standalone by default—do NOT set `standalone: true`.

## Component Structure

```typescript
import { Component, ChangeDetectionStrategy, input, output, computed } from '@angular/core';

@Component({
  selector: 'app-user-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    'class': 'user-card',
    '[class.active]': 'isActive()',
    '(click)': 'handleClick()',
  },
  template: `
    <img [src]="avatarUrl()" [alt]="name() + ' avatar'" />
    <h2>{{ name() }}</h2>
    @if (showEmail()) {
      <p>{{ email() }}</p>
    }
  `,
  styles: `
    :host { display: block; }
    :host.active { border: 2px solid blue; }
  `,
})
export class UserCard {
  // Required input
  name = input.required<string>();
  
  // Optional input with default
  email = input<string>('');
  showEmail = input(false);
  
  // Input with transform
  isActive = input(false, { transform: booleanAttribute });
  
  // Computed from inputs
  avatarUrl = computed(() => `https://api.example.com/avatar/${this.name()}`);
  
  // Output
  selected = output<string>();
  
  handleClick() {
    this.selected.emit(this.name());
  }
}
```

## Code Generation

Use Angular CLI rather than hand-writing the initial file structure.

```bash
ng generate component my-component
ng generate service my-service
ng generate directive my-directive
ng generate pipe my-pipe
```

Back to the index: [angular-component](angular-component.md)
