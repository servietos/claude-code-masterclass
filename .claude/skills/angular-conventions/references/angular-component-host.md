# Host bindings and attribute directives

## Host Bindings

Use the `host` object in `@Component`—do NOT use `@HostBinding` or `@HostListener` decorators.

```typescript
@Component({
  selector: 'app-button',
  host: {
    // Static attributes
    'role': 'button',
    
    // Dynamic class bindings
    '[class.primary]': 'variant() === "primary"',
    '[class.disabled]': 'disabled()',
    
    // Dynamic style bindings
    '[style.--btn-color]': 'color()',
    
    // Attribute bindings
    '[attr.aria-disabled]': 'disabled()',
    '[attr.tabindex]': 'disabled() ? -1 : 0',
    
    // Event listeners
    '(click)': 'onClick($event)',
    '(keydown.enter)': 'onClick($event)',
    '(keydown.space)': 'onClick($event)',
  },
  template: `<ng-content />`,
})
export class Button {
  variant = input<'primary' | 'secondary'>('primary');
  disabled = input(false, { transform: booleanAttribute });
  color = input('#007bff');
  
  clicked = output<void>();
  
  onClick(event: Event) {
    if (!this.disabled()) {
      this.clicked.emit();
    }
  }
}
```

## Attribute Directives on Components

```typescript
@Directive({
  selector: '[appHighlight]',
  host: {
    '[style.backgroundColor]': 'color()',
  },
})
export class Highlight {
  color = input('yellow', { alias: 'appHighlight' });
}

// Usage on component
@Component({
  imports: [Highlight],
  template: `<app-card appHighlight="lightblue" />`,
})
export class Page {}
```

Back to the index: [angular-component](angular-component.md)
