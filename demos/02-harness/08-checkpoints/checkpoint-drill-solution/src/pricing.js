import { findProduct } from "./catalog.js";
import { discountFor } from "./discount.js";
import { taxFor } from "./tax.js";
import { formatEur, multiply, roundCents, sum } from "./money.js";

function priceLine(item) {
  const product = findProduct(item.sku);
  const lineTotal = multiply(product.unitPrice, item.quantity);
  const discount = discountFor(item.quantity, lineTotal);
  return {
    sku: item.sku,
    name: product.name,
    quantity: item.quantity,
    unitPrice: product.unitPrice,
    lineTotal,
    discount,
    net: roundCents(lineTotal - discount)
  };
}

export function priceOrder(order) {
  const lines = order.items.map(priceLine);
  const subtotal = sum(lines.map((line) => line.lineTotal));
  const discountTotal = sum(lines.map((line) => line.discount));
  const net = roundCents(subtotal - discountTotal);
  const tax = taxFor(order.country, net);
  return {
    country: order.country,
    lines,
    subtotal,
    discountTotal,
    net,
    tax,
    total: roundCents(net + tax)
  };
}

export function renderInvoice(order) {
  const priced = priceOrder(order);
  const rows = priced.lines.map(
    (line) => `${line.name} x${line.quantity}  ${formatEur(line.net)}`
  );
  return [
    ...rows,
    `Subtotal ${formatEur(priced.subtotal)}`,
    `Discount ${formatEur(priced.discountTotal)}`,
    `Tax ${formatEur(priced.tax)}`,
    `Total ${formatEur(priced.total)}`
  ].join("\n");
}
