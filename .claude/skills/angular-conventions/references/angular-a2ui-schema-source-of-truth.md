# One Schema, Three Consumers

## Single Source of Truth

Schema drift, the catalog Zod schema, the agent system prompt, and the Angular component out of sync, is the most common production failure. Derive all three from one definition:

```text
catalog/chart-schema.ts        ← Zod schema (ground truth for valid JSON)
        ↓ imported by
catalog/custom-catalog.ts      ← registers ChartComponent + chartSchema
        ↓ same Zod schema exported as JSON Schema
agent system prompt            ← includes the JSON Schema so the LLM knows Chart fields
```

Use `register-catalogs.js` (A2UI repo `scripts/`) to resolve `$ref` imports in JSON Schema catalog files before shipping, producing a self-contained `catalog.json`. The `catalogId` URI does not require runtime fetching; catalogs must be known at compile/deploy time.

### Catalog versioning

- **Minor/patch** (same URI): add optional leaf components, add optional properties, remove properties, update metadata.
- **Major** (new URI): add/remove required properties, change property types, add container components.

Support old agents during transition by registering both catalog versions in order:

```typescript
catalogs: [inject(CustomCatalogV2), inject(CustomCatalogV1)],
```

Agents pick the best match from the ordered list.

Back to the index: [angular-a2ui](angular-a2ui.md)
