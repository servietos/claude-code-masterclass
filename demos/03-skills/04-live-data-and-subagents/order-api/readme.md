# order-api (Demo Project)

The project audited by [demo-live-context-and-fork.md](../demo-live-context-and-fork.md). It is a dependency-free order pricing service with three source files and three deliberate maintenance markers for the skills to find.

## Run It

```bash
node src/index.js
```

```text
A-1001  Northwind  net $116.85  total $140.22
A-1002  Contoso    net $524.45  total $629.34
A-1003  Fabrikam   net $22.50  total $27.00
```

## Planted Markers

| File | Line | Marker |
|---|---|---|
| `src/orders.js` | 7 | `TODO` duplicate SKUs are summed silently |
| `src/pricing.js` | 17 | `FIXME` tax rate hardcoded to domestic |
| `src/pricing.js` | 22 | `TODO` promotional codes do not stack |

## Finished Skills

The completed versions of both demo skills live in this repository's harness, not beside the project:

| Skill | Pattern |
|---|---|
| [`.claude/skills/my-order-brief`](../../../../.claude/skills/my-order-brief/SKILL.md) | Dynamic context injection, inline |
| [`.claude/skills/my-order-audit`](../../../../.claude/skills/my-order-audit/SKILL.md) | The same evidence forked to an Explore subagent |

Both reach this folder through `${CLAUDE_PROJECT_DIR}`, so they work from any directory Claude Code starts in. Invoke them from the repository root:

```text
/my-order-brief
/my-order-audit
```

Verified with Claude Code 2.1.220. `/my-order-brief` names all three markers with no tool call, because the data arrived pre-rendered. `/my-order-audit` returns only a ranked list, and its reasoning cites `taxFor`, `applyPricing`, and the `orders.js:13` call site, none of which appear in the injected text: that is the subagent having read the files in its own context.

The ranked list's formatting varies between runs; a table and a one-line-per-marker list are both correct. What must hold is that every marker is judged by impact rather than restated, and that `pricing.js:17` ranks first.
