"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = require("fs");
const path_1 = require("path");
const docx_1 = require("docx");
const VAT_RATE = 0.2;
const lineItems = [
    { description: "Consulting services (hours)", quantity: 10, unitPrice: 95 },
    { description: "Website design and development", quantity: 1, unitPrice: 1500 },
    { description: "Annual hosting and maintenance", quantity: 1, unitPrice: 300 },
];
const money = (value) => value.toFixed(2);
const text = (value, bold = false, size) => new docx_1.TextRun({ text: value, bold, size });
const paragraph = (value, options = {}) => new docx_1.Paragraph({
    alignment: options.alignment,
    spacing: { after: 120 },
    children: [text(value, options.bold, options.size)],
});
const cell = (value, alignment = docx_1.AlignmentType.LEFT, bold = false) => new docx_1.TableCell({
    children: [new docx_1.Paragraph({ alignment, children: [text(value, bold)] })],
});
const summaryRow = (label, value, bold = false) => new docx_1.TableRow({
    children: [
        new docx_1.TableCell({
            columnSpan: 3,
            children: [new docx_1.Paragraph({ alignment: docx_1.AlignmentType.RIGHT, children: [text(label, bold)] })],
        }),
        cell(value, docx_1.AlignmentType.RIGHT, bold),
    ],
});
const itemRow = (item) => new docx_1.TableRow({
    children: [
        cell(item.description),
        cell(String(item.quantity), docx_1.AlignmentType.RIGHT),
        cell(money(item.unitPrice), docx_1.AlignmentType.RIGHT),
        cell(money(item.quantity * item.unitPrice), docx_1.AlignmentType.RIGHT),
    ],
});
const subtotal = lineItems.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
const vat = subtotal * VAT_RATE;
const grandTotal = subtotal + vat;
const itemsTable = new docx_1.Table({
    width: { size: 100, type: docx_1.WidthType.PERCENTAGE },
    rows: [
        new docx_1.TableRow({
            tableHeader: true,
            children: [
                cell("Description", docx_1.AlignmentType.LEFT, true),
                cell("Quantity", docx_1.AlignmentType.RIGHT, true),
                cell("Unit Price", docx_1.AlignmentType.RIGHT, true),
                cell("Total", docx_1.AlignmentType.RIGHT, true),
            ],
        }),
        ...lineItems.map(itemRow),
        summaryRow("Subtotal", money(subtotal)),
        summaryRow("VAT (20%)", money(vat)),
        summaryRow("Grand Total", money(grandTotal), true),
    ],
});
const document = new docx_1.Document({
    sections: [
        {
            footers: {
                default: new docx_1.Footer({
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
docx_1.Packer.toBuffer(document).then((buffer) => {
    (0, fs_1.writeFileSync)((0, path_1.join)(__dirname, "..", "invoice.docx"), buffer);
});
