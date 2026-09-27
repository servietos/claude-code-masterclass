# Gate 2: the Angular wrapper trap

## Gate 2 — The Angular wrapper trap

Most `ngx-*` / `ng-*` wrappers around a popular framework-agnostic library are one person's
side project and are dead years before the library they wrap. Measured on 2026-08-16:

| wrapper | latest | published | weekly |
| --- | --- | --- | --- |
| `ng-milkdown` | 0.0.3 | 2024-06 | 68 |
| `@ctrl/ngx-codemirror` | 7.0.0 | 2023-05 | negligible |
| `@ks89/ngx-codemirror6` | 4.0.0 | 2026-05 | 190 |
| `@mdefy/ngx-markdown-editor` | 11.1.0 | 2021-01 | negligible |

**Run gate 1 against the wrapper separately from the library.** A healthy library behind a dead
wrapper is a healthy library, and the right move is to drop the wrapper: instantiate the
framework-agnostic library directly in a component. That is usually 40 to 80 lines and it is also
the zoneless-correct pattern:

```ts
export class EditorPane {
  private readonly host = viewChild.required<ElementRef<HTMLElement>>('host');
  private view: EditorView | null = null;

  constructor() {
    afterNextRender(async () => {
      const { EditorView, basicSetup } = await import('codemirror');
      this.view = new EditorView({ parent: this.host().nativeElement, /* ... */ });
    });
    inject(DestroyRef).onDestroy(() => this.view?.destroy());
  }
}
```

A wrapper is worth keeping only when it earns its own maintenance risk: `ControlValueAccessor`
plumbing you would otherwise write, or an SSR story. Convenience alone does not.

Back to the index: [angular-dependency-evaluation](angular-dependency-evaluation.md)
