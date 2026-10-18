# Invoice Service

You are a helpful assistant for the invoice service.

## Workflow

Before every commit run `npm test` and `npm run lint`.

## Money

Amounts are stored as integer cents. Never use floating point for money, because the ledger export rejects fractions.

## Testing

Write every test with Vitest. Keep each test next to the file it covers as `<name>.test.ts`.

## Style

Keep replies short and answer only what was asked. Use headers or bullet points only when they help the reader scan the reply.

## Publishing

Never run `npm publish`: this package is private and the registry login is not configured on any dev machine.
