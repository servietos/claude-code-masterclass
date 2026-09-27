# Signal Primitives: signal, computed, linkedSignal, equality

## Core Signal APIs

### signal() - Writable State

```typescript
import { signal } from '@angular/core';

// Create writable signal
const count = signal(0);

// Read value
console.log(count()); // 0

// Set new value
count.set(5);

// Update based on current value
count.update(c => c + 1);

// With explicit type
const user = signal<User | null>(null);
user.set({ id: 1, name: 'Alice' });
```

### computed() - Derived State

```typescript
import { signal, computed } from '@angular/core';

const firstName = signal('John');
const lastName = signal('Doe');

// Derived signal - automatically updates when dependencies change
const fullName = computed(() => `${firstName()} ${lastName()}`);

console.log(fullName()); // "John Doe"
firstName.set('Jane');
console.log(fullName()); // "Jane Doe"

// Computed with complex logic
const items = signal<Item[]>([]);
const filter = signal('');

const filteredItems = computed(() => {
  const query = filter().toLowerCase();
  return items().filter(item => 
    item.name.toLowerCase().includes(query)
  );
});

const totalPrice = computed(() => 
  filteredItems().reduce((sum, item) => sum + item.price, 0)
);
```

### linkedSignal() - Dependent State with Reset

```typescript
import { signal, linkedSignal } from '@angular/core';

const options = signal(['A', 'B', 'C']);

// Resets to first option when options change
const selected = linkedSignal(() => options()[0]);

console.log(selected()); // "A"
selected.set('B');       // User selects B
console.log(selected()); // "B"
options.set(['X', 'Y']); // Options change
console.log(selected()); // "X" - auto-reset to first

// With previous value access
const items = signal<Item[]>([]);

const selectedItem = linkedSignal<Item[], Item | null>({
  source: () => items(),
  computation: (newItems, previous) => {
    // Try to preserve selection if item still exists
    const prevItem = previous?.value;
    if (prevItem && newItems.some(i => i.id === prevItem.id)) {
      return prevItem;
    }
    return newItems[0] ?? null;
  },
});
```

## Signal Equality

```typescript
// Custom equality function
const user = signal<User>(
  { id: 1, name: 'Alice' },
  { equal: (a, b) => a.id === b.id }
);

// Only triggers updates when ID changes
user.set({ id: 1, name: 'Alice Updated' }); // No update
user.set({ id: 2, name: 'Bob' }); // Triggers update
```

Back to the index: [angular-signals](angular-signals.md)
