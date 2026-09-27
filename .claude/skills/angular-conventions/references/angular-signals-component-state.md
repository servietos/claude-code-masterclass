# Component State with Signals

## Component State Pattern

```typescript
@Component({
  selector: 'app-todo-list',
  template: `
    <input [value]="newTodo()" (input)="newTodo.set($any($event.target).value)" />
    <button (click)="addTodo()" [disabled]="!canAdd()">Add</button>
    
    <ul>
      @for (todo of filteredTodos(); track todo.id) {
        <li [class.done]="todo.done">
          {{ todo.text }}
          <button (click)="toggleTodo(todo.id)">Toggle</button>
        </li>
      }
    </ul>
    
    <p>{{ remaining() }} remaining</p>
  `,
})
export class TodoList {
  // State
  todos = signal<Todo[]>([]);
  newTodo = signal('');
  filter = signal<'all' | 'active' | 'done'>('all');
  
  // Derived state
  canAdd = computed(() => this.newTodo().trim().length > 0);
  
  filteredTodos = computed(() => {
    const todos = this.todos();
    switch (this.filter()) {
      case 'active': return todos.filter(t => !t.done);
      case 'done': return todos.filter(t => t.done);
      default: return todos;
    }
  });
  
  remaining = computed(() => 
    this.todos().filter(t => !t.done).length
  );
  
  // Actions
  addTodo() {
    const text = this.newTodo().trim();
    if (text) {
      this.todos.update(todos => [
        ...todos,
        { id: crypto.randomUUID(), text, done: false }
      ]);
      this.newTodo.set('');
    }
  }
  
  toggleTodo(id: string) {
    this.todos.update(todos =>
      todos.map(t => t.id === id ? { ...t, done: !t.done } : t)
    );
  }
}
```

Back to the index: [angular-signals](angular-signals.md)
