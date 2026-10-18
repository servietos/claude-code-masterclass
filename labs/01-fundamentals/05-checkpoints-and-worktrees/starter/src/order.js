import { findItem } from "./items.js";
import { lineTotal, orderTotal } from "./totals.js";

export function buildOrder(entries) {
  const lines = entries.map((entry) => {
    const item = findItem(entry.sku);
    return {
      sku: item.sku,
      name: item.name,
      quantity: entry.quantity,
      price: item.price,
      total: lineTotal(item.price, entry.quantity)
    };
  });
  return { lines, total: orderTotal(lines) };
}
