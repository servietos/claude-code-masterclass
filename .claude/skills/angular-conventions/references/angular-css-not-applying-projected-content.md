# A rule that targets projected content, and the projector's scope

A wrapper component that projects content cannot size or lay out what is projected into it. The rule
sits in the wrapper's own stylesheet, aimed at an element inside the wrapper's own template, and still
never fires.

```css
/* ux-splitter.css, the wrapper's own stylesheet */
.ux-splitter__pane > * {
  flex: 1 1 auto;
  min-height: 0;
}
```

```html
<!-- ux-splitter.html: the pane IS the wrapper's element -->
<div class="ux-splitter__pane ux-splitter__pane--right">
  <ng-content select="[slot-right]" />
</div>

<!-- sow-tab.html: but the child was declared HERE -->
<app-ux-splitter>
  <app-sow-chat slot-right />
</app-ux-splitter>
```

Angular appends the emitting component's content attribute to the **last compound selector**, so the
rule compiles to `.ux-splitter__pane > *[_ngcontent-splitter]`. `app-sow-chat` was declared in
`sow-tab`'s template, carries `_ngcontent-sowtab`, and does not match. The pane is styled; its
projected child is not.

`:host` and `::slotted` do not rescue it: Angular's emulated encapsulation has no `::slotted`, and
`:host` addresses the wrapper, not what is inside it.

## Why this one ships

The layout comes out *nearly* right, which is worse than broken. A pane 534px tall holding a 384px
child leaves the child's bottom-aligned footer floating 150px above the pane's bottom edge. A
screenshot shows a footer at the bottom of a box and reads as correct, so the defect survives visual
review and reaches the user as "I clearly said bottom aligned".

## Fix: the projector declares the fill

```css
/* sow-tab.css, the projector */
.sow-chat-panel {
  display: block;
  flex: 1 1 auto;
  align-self: stretch;
  min-height: 0;
}
```

## Corollaries

- A wrapper's own docs may claim it gives projected children a definite height. Verify rather than
  trust the comment: the rule is syntactically fine and silently inert.
- Verify alignment by measurement, never by screenshot. `getBoundingClientRect()` on the child and
  its pane must report the same `height`; equal heights is the receipt that the stretch landed.
- Grep for an existing consumer of the same wrapper. A page where it already works carries the
  stretch rules in its own stylesheet, and that file is the answer:
  `harvest/offerings-page.css` in `worktime-ui` had it before `sow-tab.css` did.

Sibling cause, different mechanism: a class borrowed from another component's stylesheet is
[component-scope](angular-css-not-applying-component-scope.md). There the rule is in the wrong file;
here it is in the right file and still cannot reach the element.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)
