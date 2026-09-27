# Splitting a many-app rollout: copy, delegate, or ask

## Rolling it out to many apps

Migrating one app teaches the replacement map. Migrating ten more teaches where the boundary is.

### Split the work at the copy/judgement line, not per app

In a repo of sibling apps built from one template, the whole frame is usually **data driven and therefore
verbatim-portable**: nav items come from `db.json`, the demo list from an API, the title from
`environment.title`. Nothing in it names a module. That covers `src/app/shared/**`, the container component,
`app.component.*`, `src/theme/*`, `tailwind.css`, `styles.scss` and `index.html`.

Do that copy yourself, on the main thread, with `cp -r` from the reference app. It is exact and free.
Fan agents out only over what is genuinely per-app: the sample/feature components, plus one build-and-verify
agent per app afterwards. Briefing an agent to "recreate the shell" spends tokens to produce a worse copy.

Keep the per-app config edits scripted rather than delegated too: `package.json` deps, the `angular.json`
styles order and budgets, `db.json` seed rows. They are fidelity work, and a script does eleven apps in one pass.

### Code that *teaches* the library you are removing is a scope decision

A testing module built demos on Material component harnesses; an optimization module taught
`cdk/scrolling`. Removing the dependency deletes the lesson rather than the styling. Separate "uses X" from
"teaches X", and take the second back to the owner with the options priced: keep the dependency for those
demos, rewrite them against the replacement, or drop them. Ask before the sweep reaches them.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)
