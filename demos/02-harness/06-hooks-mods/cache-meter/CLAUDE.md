# CLAUDE.md

## Architecture

Domain modules live in `src/`, one file per aggregate: orders, users, payments. Shared types live in `src/types.ts` and are imported by every module. No module imports another domain module directly; anything shared moves into `src/types.ts`.

## Conventions

Every exported function takes a single options object and returns a discriminated result of the form `{ ok: true, value }` or `{ ok: false, error }`. Errors carry a snake_case code from the `ErrorCode` union. No function throws.

Identifiers are branded string types (`OrderId`, `UserId`, `PaymentId`), never bare strings. Money is always minor units as an integer, never a float.

## Testing

There is no test runner wired up in this sample. Treat every change as a review exercise: state what you would assert, and do not add a dependency to prove it.

## Workflow

Read `src/types.ts` before changing any domain module, because every result shape is defined there. Keep diffs minimal: this sample exists to be read, not refactored.
