# File Drop Zone: Styling and Tailwind-Only Variant

The stylesheet that goes with the `FileDropzone` component and its template.

`src/ui/src/app/shared/file-dropzone/file-dropzone.css` — use **bico-brand** tokens (charcoal border, mustard-gold on hover/active) rather than the raw hex below; keep the dashed-border + hover-recolor shape:

```css
.dz {
  display: flex; flex-direction: column; align-items: center; gap: .5rem;
  width: 100%; padding: 1.5rem;
  border: 1.5px dashed var(--dz-border, theme(colors.gray.300));
  border-radius: .5rem; background: transparent; cursor: pointer;
  transition: border-color .15s, background .15s, color .15s;
}
.dz:hover  { border-color: var(--dz-accent, theme(colors.amber.500)); color: var(--dz-accent); }
.dz-active { border-color: var(--dz-accent); background: var(--dz-accent-weak, theme(colors.amber.50)); color: var(--dz-accent); }
.dz-progress { width: 100%; height: 4px; background: rgb(0 0 0 / .08); border-radius: 2px; overflow: hidden; }
.dz-progress-bar { height: 100%; background: var(--dz-accent); transition: width .2s; }
```

> If the app is fully Tailwind-utility (no component CSS), express the states inline instead: `[class.border-amber-500]="dragging()" [class.bg-amber-50]="dragging()"` on the button, and drop the `.css` file.

Back to the index: [angular-file-dropzone](angular-file-dropzone.md)
