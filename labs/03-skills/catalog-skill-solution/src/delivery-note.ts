import { mkdir, readFile, writeFile } from "node:fs/promises";
import {
  AlignmentType,
  Document,
  Packer,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} from "docx";

interface Party {
  name: string;
  address: string;
  contact?: string;
}

interface Item {
  sku: string;
  description: string;
  quantity: number;
  unit: string;
}

interface DeliveryNote {
  noteNumber: string;
  date: string;
  supplier: Party;
  recipient: Party;
  items: Item[];
  remarks: string;
}

const COLUMN_WIDTHS = [1600, 4426, 1500, 1500];
const TABLE_WIDTH = COLUMN_WIDTHS.reduce((sum, width) => sum + width, 0);
const HEADER_FILL = "D9E2F3";

function partyBlock(heading: string, party: Party): Paragraph[] {
  const lines = [party.name, party.address];
  if (party.contact) {
    lines.push(`Contact: ${party.contact}`);
  }
  return [
    new Paragraph({
      spacing: { before: 240 },
      children: [new TextRun({ text: heading, bold: true })],
    }),
    ...lines.map((line) => new Paragraph({ children: [new TextRun(line)] })),
  ];
}

function cell(
  text: string,
  width: number,
  options: { bold?: boolean; alignment?: (typeof AlignmentType)[keyof typeof AlignmentType]; shaded?: boolean } = {},
): TableCell {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: options.shaded ? { type: ShadingType.CLEAR, color: "auto", fill: HEADER_FILL } : undefined,
    children: [
      new Paragraph({
        alignment: options.alignment ?? AlignmentType.LEFT,
        children: [new TextRun({ text, bold: options.bold ?? false })],
      }),
    ],
  });
}

function itemsTable(items: Item[]): Table {
  const [skuWidth, descriptionWidth, quantityWidth, unitWidth] = COLUMN_WIDTHS;
  const header = new TableRow({
    tableHeader: true,
    children: [
      cell("SKU", skuWidth, { bold: true, shaded: true }),
      cell("Description", descriptionWidth, { bold: true, shaded: true }),
      cell("Quantity", quantityWidth, { bold: true, shaded: true, alignment: AlignmentType.RIGHT }),
      cell("Unit", unitWidth, { bold: true, shaded: true }),
    ],
  });
  const rows = items.map(
    (item) =>
      new TableRow({
        children: [
          cell(item.sku, skuWidth),
          cell(item.description, descriptionWidth),
          cell(String(item.quantity), quantityWidth, { alignment: AlignmentType.RIGHT }),
          cell(item.unit, unitWidth),
        ],
      }),
  );
  const pieces = items.filter((item) => item.unit === "pcs").reduce((sum, item) => sum + item.quantity, 0);
  const totalRow = new TableRow({
    children: [
      new TableCell({
        columnSpan: 2,
        width: { size: skuWidth + descriptionWidth, type: WidthType.DXA },
        children: [
          new Paragraph({ children: [new TextRun({ text: "Total pieces", bold: true })] }),
        ],
      }),
      cell(String(pieces), quantityWidth, { bold: true, alignment: AlignmentType.RIGHT }),
      cell("pcs", unitWidth, { bold: true }),
    ],
  });
  return new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: COLUMN_WIDTHS,
    rows: [header, ...rows, totalRow],
  });
}

const note = JSON.parse(await readFile("data/delivery.json", "utf8")) as DeliveryNote;

const document = new Document({
  sections: [
    {
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "DELIVERY NOTE", bold: true, size: 36 })],
        }),
        new Paragraph({ children: [new TextRun(`Note number: ${note.noteNumber}`)] }),
        new Paragraph({ children: [new TextRun(`Date: ${note.date}`)] }),
        ...partyBlock("Supplier", note.supplier),
        ...partyBlock("Recipient", note.recipient),
        new Paragraph({ spacing: { before: 240 }, children: [] }),
        itemsTable(note.items),
        new Paragraph({
          spacing: { before: 240 },
          children: [
            new TextRun({ text: "Remarks: ", bold: true }),
            new TextRun(note.remarks),
          ],
        }),
      ],
    },
  ],
});

await mkdir("out", { recursive: true });
await writeFile("out/delivery-note.docx", await Packer.toBuffer(document));
