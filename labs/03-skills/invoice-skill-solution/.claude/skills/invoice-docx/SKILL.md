---
name: invoice-docx
description: Generate a branded invoice as a Word .docx from invoice data (customer, line items, VAT rate, payment terms). Use when the user asks to "create an invoice", "bill this customer", "generate an invoice docx", "issue an invoice for", or hands over invoice line items and wants a document back. Not for reading or editing existing Word files.
allowed-tools: Read, Write, Bash(node:*)
---

# Invoice as a Word document

Today is !`date +%Y-%m-%d`, which is the issue date unless the user names another one.

## Inputs

Collect these before rendering. Ask only for what is missing; never invent a VAT ID, an IBAN, or an amount.

| Field | Notes |
|---|---|
| `number` | Invoice number. If the user has no scheme, use `INV-<year>-<4-digit sequence>` |
| `issued`, `due` | ISO dates. Default `due` to 14 days after `issued` |
| `currency`, `taxRate` | `taxRate` is a fraction, `0.2` for 20% |
| `seller`, `buyer` | Each with `name`, `address`, `vatId`; the seller also carries `iban` |
| `lines` | One entry per position: `description`, `quantity`, `unitPrice` |

## Steps

1. Write the collected fields to `data/<number>.json` in the shape shown in [references/invoice-layout.md](references/invoice-layout.md).
2. Render it: `node .claude/skills/invoice-docx/scripts/render.mjs data/<number>.json out/<number>.docx`
3. Report the output path and the three totals the renderer computed (net, VAT, gross). Do not recompute them yourself in the reply.

The renderer owns the layout and the arithmetic. When the user wants a different look, edit `scripts/render.mjs`, never the numbers in the reply.

## Examples

"Invoice Nordwind for two days of training at 3200 a day" collects the buyer, one line item at quantity 2, and the seller from the last invoice in `data/`, then renders.

"Same invoice but 10% VAT" rewrites `taxRate` in the JSON and re-renders; it does not edit the .docx.

## Troubleshooting

`Cannot find package 'docx'` means dependencies are missing: run `npm install` in the folder that holds `package.json`.

An invoice that renders with `EUR NaN` means a `quantity` or `unitPrice` arrived as a string. Fix the JSON, not the renderer.
