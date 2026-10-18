import { writeFileSync } from "fs";
import { join } from "path";
import {
  AlignmentType,
  Document,
  Footer,
  Packer,
  Paragraph,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} from "docx";

type Alignment = (typeof AlignmentType)[keyof typeof AlignmentType];

interface LineItem {
  description: string;
  quantity: number;
  unitPrice: number;
}

const VAT_RATE = 0.2;

const lineItems: LineItem[] = [
  { description: "Consulting services (hours)", quantity: 10, unitPrice: 95 },
  { description: "Website design and development", quantity: 1, unitPrice: 1500 },
  { description: "Annual hosting and maintenance", quantity: 1, unitPrice: 300 },
];

const money = (value: number): string => value.toFixed(2);

const text = (value: string, bold = false, size?: number): TextRun =>
  new TextRun({ text: value, bold, size });

const paragraph = (value: string, options: { bold?: boolean; size?: number; alignment?: Alignment } = {}): Paragraph =>
  new Paragraph({
    alignment: options.alignment,
    spacing: { after: 120 },
    children: [text(value, options.bold, options.size)],
  });

const cell = (value: string, alignment: Alignment = AlignmentType.LEFT, bold = false): TableCell =>
  new TableCell({
    children: [new Paragraph({ alignment, children: [text(value, bold)] })],
  });

const summaryRow = (label: string, value: string, bold = false): TableRow =>
  new TableRow({
    children: [
      new TableCell({
        columnSpan: 3,
        children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [text(label, bold)] })],
      }),
      cell(value, AlignmentType.RIGHT, bold),
    ],
  });

const itemRow = (item: LineItem): TableRow =>
  new TableRow({
    children: [
      cell(item.description),
      cell(String(item.quantity), AlignmentType.RIGHT),
      cell(money(item.unitPrice), AlignmentType.RIGHT),
      cell(money(item.quantity * item.unitPrice), AlignmentType.RIGHT),
    ],
  });

const subtotal = lineItems.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
const vat = subtotal * VAT_RATE;
const grandTotal = subtotal + vat;

const itemsTable = new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell("Description", AlignmentType.LEFT, true),
        cell("Quantity", AlignmentType.RIGHT, true),
        cell("Unit Price", AlignmentType.RIGHT, true),
        cell("Total", AlignmentType.RIGHT, true),
      ],
    }),
    ...lineItems.map(itemRow),
    summaryRow("Subtotal", money(subtotal)),
    summaryRow("VAT (20%)", money(vat)),
    summaryRow("Grand Total", money(grandTotal), true),
  ],
});

const document = new Document({
  sections: [
    {
      footers: {
        default: new Footer({
          children: [paragraph("Payment due within 30 days")],
        }),
      },
      children: [
        paragraph("INVOICE", { bold: true, size: 48 }),
        paragraph("Invoice number: INV-2024-001"),
        paragraph("Date: 2024-01-15"),
        paragraph("Bill To", { bold: true }),
        paragraph("Northwind Logistics GmbH"),
        paragraph("Hauptstrasse 12"),
        paragraph("1010 Wien, Austria"),
        paragraph(""),
        itemsTable,
      ],
    },
  ],
});

Packer.toBuffer(document).then((buffer) => {
  writeFileSync(join(__dirname, "..", "invoice.docx"), buffer);
});
