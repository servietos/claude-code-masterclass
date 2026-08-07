# Components

Standalone components only. Set `changeDetection: ChangeDetectionStrategy.OnPush` on every component and take dependencies through `inject()` rather than constructor parameters.

Template state comes from signals, so a component never subscribes in `ngOnInit` and never calls `markForCheck()` by hand.
