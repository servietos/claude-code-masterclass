# Reporting the verdict and the completion checklist

## Verdict shape

Report a decision, not a survey: **the call, the reason it beat the runner-up, the two measured
numbers, and the cost in hours.** Put the maintenance table and the size table in the reply only
because they are the evidence for the call, and put the task breakdown in the repo's todo file
rather than the reply.

## Checklist

- [ ] Health read from `registry.npmjs.org` + `api.npmjs.org`, not from npmjs.com or a summary.
- [ ] Latest publish date checked, not just download count.
- [ ] Any framework wrapper health-checked separately from the library it wraps.
- [ ] Size measured with esbuild + gzip on the real import surface, not estimated.
- [ ] App's current initial bundle measured as the headroom baseline.
- [ ] Eager-vs-lazy decided explicitly; heavy libs put behind `import()`.
- [ ] Format-fidelity gate run for anything that parses or serializes stored content.
- [ ] Verdict reported with numbers; task breakdown written to the repo's todo file.

Back to the index: [angular-dependency-evaluation](angular-dependency-evaluation.md)
