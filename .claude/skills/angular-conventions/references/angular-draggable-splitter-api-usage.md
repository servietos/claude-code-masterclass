# Splitter host usage and inputs

## Host usage

```html
<ux-splitter storageKey="my-view-split" [initial]="416" [min]="320" [max]="640">
  <div slot-left>…primary content…</div>
  <div slot-right>…side panel…</div>
</ux-splitter>
```

- **Unique `storageKey` per usage site** (`home-split`, `edit-split`, …) so pages
  don't share a persisted width.
- Import the standalone component into the host's `imports`.

## API

```html
<ux-splitter storageKey="edit-task-split" [initial]="416" [min]="320" [max]="640">
  <div slot-left> …chat card… </div>
  <div slot-right> …right panel… </div>
</ux-splitter>
```

Inputs: `storageKey` (**required**, unique per usage site), `initial` (320),
`min` (200), `max` (560), `step` (16, px per Arrow key). Import
`SplitterComponent` into the host's `imports`. Content projects two panes by
attribute selector: `[slot-left]` / `[slot-right]`.


Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)
