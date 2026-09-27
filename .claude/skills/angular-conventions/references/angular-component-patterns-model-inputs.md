# Model Inputs and Two-Way Binding

## Model Inputs (Two-Way Binding)

For two-way binding with `[(value)]` syntax:

```typescript
import { Component, model } from '@angular/core';

@Component({
  selector: 'app-slider',
  host: {
    '(input)': 'onInput($event)',
  },
  template: `
    <input 
      type="range" 
      [value]="value()" 
      [min]="min()" 
      [max]="max()" 
    />
    <span>{{ value() }}</span>
  `,
})
export class Slider {
  // Model creates both input and output
  value = model(0);
  min = input(0);
  max = input(100);
  
  onInput(event: Event) {
    const target = event.target as HTMLInputElement;
    this.value.set(Number(target.value));
  }
}

// Usage: <app-slider [(value)]="sliderValue" />
```

Required model:

```typescript
value = model.required<number>();
```

Back to the index: [angular-component-patterns](angular-component-patterns.md)
