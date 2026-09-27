# Material to Tailwind replacement map

## Replacement map

| Material | Replacement |
|---|---|
| `<mat-card>` + parts | `div.card` / `.card-header` / `h2.card-title` / `.card-content` / `.card-actions` |
| `mat-raised-button`, `mat-flat-button` | `class="btn btn-primary"` |
| `mat-stroked-button` | `class="btn btn-outline"` |
| `mat-icon-button` | `class="btn-icon"` |
| `mat-mini-fab` | `class="btn-fab"` |
| `<mat-form-field>` + `<mat-label>` + `matInput` | `div.field` + `label.label` + `input.input` |
| `<mat-slide-toggle>` | small shared component wrapping `input[type=checkbox].sr-only` + a track/thumb span |
| `<mat-checkbox>` | `label.checkbox` around a native checkbox with `accent-color` |
| `<mat-button-toggle-group>` | `div.toggle-group` + `button.toggle-btn` with `[class.active]` |
| `<mat-progress-bar>` | shared component; indeterminate is a `@keyframes` sweep on left/right |
| `<mat-tab-group>` | `div.tabs` + `button.tab` driven by a `signal` and `@switch` |
| `<mat-expansion-panel>` | `div.panel` + `button.panel-header` + `@if` |
| `<mat-table>` | plain `<table class="data-table">` |
| `<mat-toolbar>` | a frame class per position, never one generic `.toolbar` |
| `<mat-sidenav-container>` | flex row: `aside` + content column; `over` mode is a positioned class plus a backdrop div |
| `<mat-icon>x</mat-icon>` | `<span class="icon">x</span>`; the Material Icons **font** is a Google font and can stay in `index.html` |
| `matTooltip` | CSS-only `.tip` using `content: attr(data-tip)` on `::after` |
| `MatSnackBar` | signal-based service + a small component in the shell |
| `MatDrawerMode` | local `export type DrawerMode = 'over' \| 'side'` |
| `BreakpointObserver` | `window.matchMedia(...)`, guarded |
| `CdkTextareaAutosize` | usually unnecessary; a flex-filling textarea is better (see below) |

Name the toolbar classes by position (`topbar`, `page-header`, `app-toolbar`), never `.toolbar`:
component SCSS in these apps frequently already defines `.toolbar` for a local button row, and a
global `.toolbar` collides with it in a way that only shows up as a stray background colour.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)
