import { readFile, writeFile } from "node:fs/promises";
import {
  AlignmentType,
  Document,
  HeadingLevel,
  Packer,
  Paragraph,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} from "docx";

const money = (value, currency) => `${currency} ${value.toFixed(2)}`;

const cell = (text, alignment = AlignmentType.LEFT) =>
  new TableCell({
    children: [new Paragraph({ alignment, children: [new TextRun(text)] })],
  });

const headerCell = (text, alignment = AlignmentType.LEFT) =>
  new TableCell({
    children: [new Paragraph({ alignment, children: [new TextRun({ text, bold: true })] })],
  });

export function buildInvoice(invoice) {
  const net = invoice.lines.reduce((sum, line) => sum + line.quantity * line.unitPrice, 0);
  const tax = net * invoice.taxRate;
  const gross = net + tax;

  const lineRows = invoice.lines.map(
    (line) =>
      new TableRow({
        children: [
          cell(line.description),
          cell(String(line.quantity), AlignmentType.RIGHT),
          cell(money(line.unitPrice, invoice.currency), AlignmentType.RIGHT),
          cell(money(line.quantity * line.unitPrice, invoice.currency), AlignmentType.RIGHT),
        ],
      })
  );

  const table = new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [
      new TableRow({
        children: [
          headerCell("Description"),
          headerCell("Qty", AlignmentType.RIGHT),
          headerCell("Unit price", AlignmentType.RIGHT),
          headerCell("Amount", AlignmentType.RIGHT),
        ],
      }),
      ...lineRows,
    ],
  });

  const totals = [
    ["Net", net],
    [`VAT ${(invoice.taxRate * 100).toFixed(0)}%`, tax],
    ["Total", gross],
  ].map(
    ([label, value]) =>
      new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: `${label}: ${money(value, invoice.currency)}`, bold: label === "Total" })],
      })
  );

  return new Document({
    sections: [
      {
        children: [
          new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(`Invoice ${invoice.number}`)] }),
          new Paragraph({ children: [new TextRun(`Issued ${invoice.issued}, due ${invoice.due}`)] }),
          new Paragraph({ children: [new TextRun("")] }),
          new Paragraph({ children: [new TextRun({ text: invoice.seller.name, bold: true })] }),
          new Paragraph({ children: [new TextRun(invoice.seller.address)] }),
          new Paragraph({ children: [new TextRun(`VAT ID ${invoice.seller.vatId}, IBAN ${invoice.seller.iban}`)] }),
          new Paragraph({ children: [new TextRun("")] }),
          new Paragraph({ children: [new TextRun({ text: `Bill to: ${invoice.buyer.name}`, bold: true })] }),
          new Paragraph({ children: [new TextRun(invoice.buyer.address)] }),
          new Paragraph({ children: [new TextRun(`VAT ID ${invoice.buyer.vatId}`)] }),
          new Paragraph({ children: [new TextRun("")] }),
          table,
          new Paragraph({ children: [new TextRun("")] }),
          ...totals,
        ],
      },
    ],
  });
}

export async function renderInvoice(invoice) {
  return Packer.toBuffer(buildInvoice(invoice));
}

const [dataPath, outPath] = process.argv.slice(2);

if (dataPath && outPath) {
  const invoice = JSON.parse(await readFile(dataPath, "utf8"));
  await writeFile(outPath, await renderInvoice(invoice));
  console.log(`wrote ${outPath}`);
}
