# Compact Pickers For Large Option Sets

## Large Option Sets Need a Custom Compact Component

`ChoicePicker` from `BasicCatalog` has no dropdown or compact variant. Confirmed from the shipped `.d.ts` (`ChoicePickerApi` in `@a2ui/web_core/src/v0_9/basic_catalog/components/basic_components.d.ts`): `variant` only accepts `"multipleSelection" | "mutuallyExclusive"`, both of which render as a full vertical list of checkboxes or radio buttons. There is no schema option that collapses it into a `<select>`.

**Rule of thumb:** for any bound field where the option count is unbounded or plausibly large (contact lists, account/category lists, anything sourced from a DB query rather than a fixed small enum), do not reach for `ChoicePicker`. Build a small custom catalog component wrapping a native `<select>` (or similar compact control) from the start, rather than discovering the UX problem after a real user scrolls past 30 radio buttons to find the Save button.

### Worked example: `Select`

vouchers-ai hit this with an "Account" picker driven by ~30 expense accounts pulled from the DB.

- **Schema** — `src/vouchers-ui/src/app/assistant/catalog/select/select-schema.ts`:

  ```typescript
  import { z } from 'zod';
  import { DynamicStringSchema } from '@a2ui/web_core/v0_9';

  export const selectSchema = z.object({
    label: DynamicStringSchema.optional(),
    value: DynamicStringSchema,
    options: z.array(
      z.object({
        value: z.string(),
        label: DynamicStringSchema,
      }),
    ),
  }).strict();
  ```

  The `options` shape (`{ value: string; label: DynamicString }[]`) deliberately matches `ChoicePickerApi.options`, confirmed from the same `.d.ts`, so swapping a `ChoicePicker` prompt template over to `Select` is a one-word change in the agent system prompt (see below).

- **Component** — `src/vouchers-ui/src/app/assistant/catalog/select/select.ts` (+ separate `select.html` / `select.css`, this project never inlines templates/styles): extends `CatalogComponent` from `@a2ui/angular/v0_9`, reads `props()['value']?.value()` / `props()['options']?.value()` the same way `TextFieldComponent` and `ChoicePickerComponent` do internally, and writes back via `props()['value']?.onUpdate(newValue)` on the native `<select>`'s `(change)` event.

- **Catalog registration** — `src/vouchers-ui/src/app/assistant/catalog/custom-catalog.ts`: a `CustomCatalog extends BasicCatalogBase` with `extraComponents: [selectEntry]`, wired into `A2UI_RENDERER_CONFIG` in `app.config.ts` in place of a plain `inject(BasicCatalog)`. This keeps every default BasicCatalog component (`Card`, `Column`, `Text`, `TextField`, `DateTimeInput`, `Button`, …) available — `BasicCatalogBase` merges `DEFAULT_COMPONENT_IMPLEMENTATIONS` with `extraComponents`, it does not replace them.

### Prompt-template lesson: literal fill-in-the-blank beats prose

The agent system prompt that emits this component's JSON (`src/vouchers-ai/Services/A2uiAgentService.cs`) builds the `updateComponents` message as a literal fill-in-the-blank JSON template in the system prompt string, not a prose description of the shape. This is deliberate: prose lets the LLM invent or rename keys (for example emitting `"type"` instead of `"component"`) even at temperature 0. Swapping `ChoicePicker` for a new custom component in that prompt is a one-line change to the template (`"component":"Select"` instead of `"component":"ChoicePicker"`) — keep it that way for any future custom component; do not refactor the template into a descriptive paragraph.

Back to the index: [angular-a2ui](angular-a2ui.md)
