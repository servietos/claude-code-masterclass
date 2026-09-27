# Known-benign noise during an update

## 8. Known-benign noise, do not chase

### 8. Known-benign noise, do not chase

- A clean `npm i -g @angular/cli` still emits an `ERESOLVE` peer warning for `listr2`: CLI 22.1.3 depends on `listr2@10.2.2` while its own `@listr2/prompt-adapter-inquirer@4.2.4` pins `10.2.1`. No version combination resolves it and nothing is broken.
- `npm audit` reports 3 moderate findings via `@angular/cli` to `@modelcontextprotocol/sdk` to `@hono/node-server`. That is the CLI's own MCP server, never in the shipped browser bundle, and `npm audit fix --force` "fixes" it by **downgrading** `@angular/cli` to 21.0.4. Leave it.
- `mcp__angular-cli__search_documentation` may fail with `Cannot find module 'algoliasearch'` from the globally installed CLI. `list_projects` and `get_best_practices` still work; fall back to on-disk peer ranges and the npm registry for version questions.

Back to the index: [angular-update](angular-update.md)
