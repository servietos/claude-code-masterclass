# Invoice data shape and layout

The renderer reads one JSON file and writes one `.docx`. This is the contract between them.

## Data shape

```json
{
  "number": "INV-2026-0042",
  "issued": "2026-07-29",
  "due": "2026-08-12",
  "currency": "EUR",
  "taxRate": 0.2,
  "seller": {
    "name": "Integrations GmbH",
    "address": "Hauptstrasse 12, 1010 Wien",
    "vatId": "ATU12345678",
    "iban": "AT61 1904 3002 3457 3201"
  },
  "buyer": {
    "name": "Nordwind Handels GmbH",
    "address": "Ringstrasse 4, 5020 Salzburg",
    "vatId": "ATU87654321"
  },
  "lines": [
    { "description": "Claude Code masterclass, two days", "quantity": 2, "unitPrice": 3200 }
  ]
}
```

`quantity` and `unitPrice` are numbers, never strings. `taxRate` is a fraction.

## Document layout

| Block | Content |
|---|---|
| Heading 1 | `Invoice <number>` |
| Line under it | `Issued <issued>, due <due>` |
| Seller block | Name in bold, address, then `VAT ID <vatId>, IBAN <iban>` |
| Buyer block | `Bill to: <name>` in bold, address, `VAT ID <vatId>` |
| Table | Description, Qty, Unit price, Amount. Header row bold, the three numeric columns right-aligned |
| Totals | Right-aligned `Net`, `VAT <rate>%`, and `Total`, with `Total` bold |

## Arithmetic

Amount per line is `quantity * unitPrice`. Net is the sum of the line amounts, VAT is `net * taxRate`, gross is `net + tax`. All three are formatted as `<currency> <value with two decimals>`.
