# Authoring A Custom Catalog Component

## Defining a custom component

### Defining a custom component

Each custom component needs three files: a Zod schema, an Angular component, and a catalog entry object.

**Schema**, defines valid JSON the agent can emit for this component:

```typescript
// chart/chart-schema.ts
import { z } from 'zod';
import { DynamicStringSchema } from '@a2ui/web_core/v0_9';

export const chartSchema = z.object({
  title:     DynamicStringSchema,
  dataPath:  z.string(),
  chartType: z.enum(['bar', 'line', 'pie']).optional(),
}).strict();

export type ChartSchema = z.infer<typeof chartSchema>;
```

`DynamicStringSchema` (confirmed export from `@a2ui/web_core/v0_9`, defined in `schema/common-types.d.ts`) is a Zod union of a literal string, a `{ path: string }` binding, and a `{ call, args, returnType }` function call. It is the real mechanism for "this field accepts either a literal or a data-model path reference" — there is no `binding()` helper in the package. Matching `DynamicNumberSchema` / `DynamicBooleanSchema` / `DynamicStringListSchema` exist for the other primitive shapes.

**Angular component**, receives props via signal inputs:

```typescript
// chart/chart.ts
import {
  Component, ChangeDetectionStrategy,
  input, computed,
} from '@angular/core';
import type { BoundProperty } from '@a2ui/web_core/v0_9';

interface ChartProps {
  title:     BoundProperty<string>;
  dataPath:  string;
  chartType?: 'bar' | 'line' | 'pie';
}

const initialProps: ChartProps = {
  title:    { value: () => '' },
  dataPath: '',
};

@Component({
  selector: 'app-chart',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <figure>
      <figcaption>{{ title() }}</figcaption>
      <!-- chart canvas wired here -->
    </figure>
  `,
})
export class ChartComponent {
  // Provided by the A2UI renderer; default needed for initial render pass
  readonly props          = input<ChartProps>(initialProps);
  readonly surfaceId      = input.required<string>();
  readonly componentId    = input.required<string>();
  readonly dataContextPath = input('/');

  // BoundProperty<T>.value() is a signal accessor, use computed() to derive
  protected readonly title = computed(() => this.props().title.value());
}
```

**Catalog entry:**

```typescript
// chart/chart.ts (continued)
import type { AngularComponentImplementation } from '@a2ui/angular/v0_9';
import { chartSchema } from './chart-schema';

export const chartEntry = {
  name:      'Chart',          // must match the string agents use in "component"
  component: ChartComponent,
  schema:    chartSchema,
} as unknown as AngularComponentImplementation;
```

### Schema-to-component correspondence

The catalog schema is the contract. Every property the schema defines must be handled by the Angular component, and vice versa.

| Zod schema field | Angular component usage | Agent JSON |
|---|---|---|
| `title: DynamicStringSchema` | `computed(() => props().title.value())` | `"title": {"path": "/report/name"}` |
| `chartType: z.enum([...])` | `props().chartType` (direct, not bound) | `"chartType": "bar"` |
| `dataPath: z.string()` | `props().dataPath` | `"dataPath": "/sales/2026"` |

Back to the index: [angular-a2ui](angular-a2ui.md)
