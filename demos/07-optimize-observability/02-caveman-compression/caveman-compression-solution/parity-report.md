# Parity Report: CLAUDE.verbose.md vs CLAUDE.caveman.md

## Token Counts

| File | Tokens |
|------|-------:|
| CLAUDE.verbose.md | 1726 |
| CLAUDE.caveman.md | 766 |
| Reduction | 56% |

Source: `count-tokens.ts` (js-tiktoken, cl100k_base). Recorded in `baseline.txt`.

## Summary

40 rules compared. 37 kept at the same strength. 2 strengthened (advice became a must). 1 weakened (lost its modal).

## Rule-by-Rule Comparison

Status key: **Kept** = same rule and strength. **Strengthened** = original advisory, caveman mandatory. **Weakened** = original mandatory, caveman descriptive.

### Project Overview

| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 1 | Work within project requirements and constraints; respect architecture decisions. | Stay within project requirements and constraints. Respect architecture decisions in all work. | Kept |
| 2 | Keep the dual teaching purpose in mind when modifying code or docs. | Keep dual purpose in mind when changing code or docs. | Kept |

### Architecture and File Layout

| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 3 | Keep route handlers, schemas, and bootstrap logic in separate files; do not intermix. | Keep route handlers, schema definitions, server bootstrap in separate files. Never mix them. | Kept |
| 4 | `src/server.ts` bootstraps the Fastify instance and registers route plugins. | `src/server.ts` bootstraps Fastify instance and registers route plugins. | Kept |
| 5 | Route modules live in feature subdirectories under `src/`. | Route modules live in feature subdirectories under `src/`. | Kept |
| 6 | Each feature directory has `schema.ts` and `router.ts`. | Each feature directory: schemas in `schema.ts`. Handlers in `router.ts`. | Kept |
| 7 | Do not place schemas in router files. | Never place schemas in router files. | Kept |
| 8 | Consider new subdirectories per feature, following `users/`. | Prefer new subdirectories for new features, following `users/` feature directory. | Kept |

### File Naming Conventions

| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 9 | TypeScript source uses `.ts`, lives in `src/`; top-level utility scripts stay clearly distinguishable. | All TypeScript source files: `.ts` extension, inside `src/` or subdirectory. Top-level utility scripts may use `.ts`, but mark them clearly by placement and naming. | Kept |
| 10 | Use the patterns `router.ts`, `schema.ts`, `server.ts`, `*.test.ts`. | Same four patterns, each with its purpose. | Kept |
| 11 | Consider kebab-case directories and camelCase identifiers. | Prefer kebab-case directory names, camelCase identifiers. | Kept |
| 12 | Never use abbreviations in file or directory names. | Never abbreviate file or directory names. | Kept |
| 13 | Co-locate tests with source, same base name plus `.test.ts`. | Always co-locate tests with source, same base name plus `.test.ts`. | Kept |

### Error Handling

| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 14 | Do not write custom try-catch around validation logic. | Never write custom try-catch around validation logic. | Kept |
| 15 | `@fastify/type-provider-zod` validates from the route `schema`; failures return 400 with a descriptive message. | Validates from route `schema` object. Failures return 400 with descriptive message. | Kept |
| 16 | Leverage built-in validation as extensively as possible. | Prefer this built-in validation everywhere. | Kept |
| 17 | Let Fastify's built-in handler catch and format runtime errors. | Let Fastify's built-in error handler format them. | Kept ("catch" dropped) |
| 18 | Add custom error handlers only to transform or enrich responses the default cannot handle. | Add custom error handlers only to transform or enrich responses default handler cannot handle. | Kept |
| 19 | Custom error handling must not swallow errors silently. | Custom error handling must never swallow errors silently. | Kept |

### Testing Requirements

| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 20 | New route handlers: Vitest tests for happy path plus at least one edge or error case. | Same. | Kept |
| 21 | Use Fastify `inject` for test requests. | Use Fastify `inject` for test requests. | Kept |
| 22 | Consider testing pagination explicitly on pagination routes. | Routes with pagination: test pagination explicitly. | **Strengthened** |
| 23 | Tests live in `.test.ts` files. | Tests live in `.test.ts` files. | Kept |
| 24 | Each test file uses `beforeAll` and `afterAll` to init and close the Fastify instance. | Same. | Kept |
| 25 | Avoid sharing mutable state between tests. | Never share mutable state between tests. | Kept |
| 26 | Consider running the full suite before committing. | Prefer running full test suite before commits. | Kept |

### Code Style

| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 27 | Strict TypeScript per `tsconfig.json`. | Strict TypeScript per `tsconfig.json`. | Kept |
| 28 | Avoid `any`, non-null assertions, and other escape hatches. | Never use `any`, non-null assertions, or other escape hatches. | Kept |
| 29 | Export Zod schemas with `z.infer` types. | Export Zod schemas with inferred types via `z.infer`. | Kept |
| 30 | Consider `z.coerce` for numeric query params. | Prefer `z.coerce` for numeric query params. | Kept (coercion rationale dropped) |
| 31 | Keep functions and handlers concise, single responsibility. | Single responsibility, concise. | Kept |
| 32 | Consider extracting helpers when functions exceed ~30 lines. | Extract helpers past ~30 lines. | **Strengthened** |
| 33 | Use ES module syntax (`import`/`export`) only. | Use ES modules (`import`/`export`) only. | Kept |
| 34 | `"type": "module"` in `package.json`; CommonJS `require` breaks. | Same. | Kept |
| 35 | Consider `async/await` over Promise chains or callbacks. | Prefer `async/await` over Promise chains or callbacks. | Kept |

### Git Workflow

| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 36 | Run `npm test` (full Vitest suite) before committing. | Always run full Vitest suite with `npm test` before committing. | Kept |
| 37 | Do not commit if any test fails. | Never commit while any test fails. | Kept |
| 38 | Be sure to write commit messages that clearly describe purpose and intent, not the files modified. | Commit messages state purpose and intent, not file list. | **Weakened** (no modal; reads as description) |
| 39 | Consider one logical change per commit. | Prefer one logical change per commit. | Kept |
| 40 | Small commits: easier review, easier revert, cleaner history. | Easier review, easier revert, cleaner history. | Kept |

## Missing Rules

None. Every rule in the original has a counterpart in the caveman file.

## Weakened Rules

- **#38 Commit messages.** The original is a must. The caveman line has no modal and reads as description. Suggested fix: "Always write commit messages stating purpose and intent."

## Strengthened Rules (break "same enforceability")

- **#22 Pagination tests.** Original is advisory. Suggested fix: "Prefer testing pagination explicitly on pagination routes."
- **#32 Helper extraction.** Original is advisory. Suggested fix: "Prefer extracting helpers past ~30 lines."

## Rationale Dropped (rules intact)

- #17: "catch" removed from the error-handler line.
- #30: why coercion is needed (query strings are always strings, so numeric params need coercion) is trimmed to "Query strings are always strings."
- Overview: "highly performant" removed.

## Status

The caveman file has not been edited. The three suggested fixes (#22, #32, #38) are pending your go-ahead.
