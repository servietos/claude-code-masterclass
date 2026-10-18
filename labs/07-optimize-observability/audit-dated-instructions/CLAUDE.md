# Invoice Service

You are a helpful assistant for the invoice service.

## Workflow

IMPORTANT: You MUST think step by step before every answer. Be extremely thorough. Do not be lazy.

CRITICAL: NEVER skip the checks. Before every commit run `npm run verify` and `npm run lint`. Do not stop early.

## Money

Amounts are stored as integer cents. Never use floating point for money, because the ledger export rejects fractions.

## Testing

Write every test with Vitest. Keep each test next to the file it covers as `<name>.test.ts`.

## Style

Never use headers or bullet points in your replies. Keep every answer under 40 words.

## Publishing

Never run `npm publish`: this package is private and the registry login is not configured on any dev machine.
