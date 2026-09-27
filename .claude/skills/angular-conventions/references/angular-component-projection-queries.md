# Content projection, view queries and content queries

## Content Projection

```typescript
@Component({
  selector: 'app-card',
  template: `
    <header>
      <ng-content select="[card-header]" />
    </header>
    <main>
      <ng-content />
    </main>
    <footer>
      <ng-content select="[card-footer]" />
    </footer>
  `,
})
export class Card {}

// Usage:
// <app-card>
//   <h2 card-header>Title</h2>
//   <p>Main content</p>
//   <button card-footer>Action</button>
// </app-card>
```

## View Queries

Query elements and components in the template:

```typescript
import { Component, viewChild, viewChildren, ElementRef } from '@angular/core';

@Component({
  selector: 'app-gallery',
  template: `
    <div #container class="gallery">
      @for (image of images(); track image.id) {
        <app-image-card [image]="image" />
      }
    </div>
  `,
})
export class Gallery {
  images = input.required<Image[]>();

  // Query single element
  container = viewChild.required<ElementRef<HTMLDivElement>>('container');

  // Query single component (optional)
  firstCard = viewChild(ImageCard);

  // Query all matching components
  allCards = viewChildren(ImageCard);
}
```

## Content Queries

Query projected content:

```typescript
import { Component, contentChild, contentChildren, effect, signal } from '@angular/core';

@Component({
  selector: 'app-tabs',
  template: `
    <div class="tab-headers">
      @for (tab of tabs(); track tab.label()) {
        <button
          [class.active]="tab === activeTab()"
          (click)="selectTab(tab)"
        >
          {{ tab.label() }}
        </button>
      }
    </div>
    <div class="tab-content">
      <ng-content />
    </div>
  `,
})
export class Tabs {
  // Query all projected Tab children
  tabs = contentChildren(Tab);

  // Query single projected element
  header = contentChild('tabHeader');

  activeTab = signal<Tab | undefined>(undefined);

  constructor() {
    // Set first tab as active when tabs are available
    effect(() => {
      const firstTab = this.tabs()[0];
      if (firstTab && !this.activeTab()) {
        this.activeTab.set(firstTab);
      }
    });
  }

  selectTab(tab: Tab) {
    this.activeTab.set(tab);
  }
}

@Component({
  selector: 'app-tab',
  template: `<ng-content />`,
  host: {
    '[class.active]': 'isActive()',
    '[style.display]': 'isActive() ? "block" : "none"',
  },
})
export class Tab {
  label = input.required<string>();
  isActive = input(false);
}
```

Back to the index: [angular-component](angular-component.md)
