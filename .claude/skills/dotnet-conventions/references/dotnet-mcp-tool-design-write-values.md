# Who owns the numbers on a write: proposal verbatim, entity-derived fields

## Propose/confirm tool pairs: the confirming leg never recomputes

A server that writes on the model's behalf usually ships two tools: one that proposes (returns a
plain-text description and asks for a yes) and one that confirms and writes. The trap is running the
same resolver on both legs.

A private receipt of 57.90 gross was proposed correctly as `Net 57.90 / VAT 0%`. The confirming tool
took `netAmount` plus the VAT the model had read off the receipt, ran the same
`net * (1 + vat/100)` derivation, and wrote 63.69. Nothing errored, the suite was green, and the
ledger was 5.79 over the receipt.

Rules:

- **The confirming leg takes the proposal verbatim.** Make it explicit at the call site rather than
  implicit in a number: an `amountMode: Final | Recompute` argument on the shared resolver, where
  `Final` means the amount supplied is already the total.
- **Require, do not default, the fields the proposal already decided.** A confirming input that
  defaults VAT is guessing: `0` silently destroys an input-tax deduction and `20` invents one. Refuse
  the row with a message naming the proposal instead, and refuse only that row, not the batch.
- **Both legs must round-trip.** Feed the proposal's own printed values back into the confirming tool
  in a test and assert the written amounts equal the proposed ones.
- Descriptions on the two tools must not contradict each other. "The VAT printed on the receipt"
  belongs on the proposing tool; the confirming tool's field is "the VAT shown in the proposal".

## Let the resolved entity decide the derived fields, not the caller

When a tool's arguments could contradict each other, derive from the one the server can verify. An
expense-booking tool took `account`, `vatPercentage` and a voucher type; a private account can never
carry input tax, so VAT and voucher type are properties of the resolved account, not of the caller's
arguments. Deriving them server-side made an invalid combination unrepresentable and reduced the
model's job to a single account choice.

The matching risk: once accounts of both kinds share one candidate list, a name-fragment match can
silently cross the boundary. Require an exact id for the sensitive kind on any path that writes
without human confirmation, and let the fragment match stand where a human confirms first.

Back to the index: [dotnet-mcp-tool-design](dotnet-mcp-tool-design.md)
