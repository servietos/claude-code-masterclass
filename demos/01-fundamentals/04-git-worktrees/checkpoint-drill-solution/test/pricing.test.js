import test from "node:test";
import assert from "node:assert/strict";
import { priceOrder, renderInvoice } from "../src/pricing.js";

const smallOrder = {
  country: "DE",
  items: [{ sku: "seat-standard", quantity: 4 }]
};

const tieredOrder = {
  country: "AT",
  items: [
    { sku: "seat-standard", quantity: 100 },
    { sku: "storage-block", quantity: 10 }
  ]
};

test("priceOrder prices a single line without a discount", () => {
  const result = priceOrder(smallOrder);
  assert.equal(result.subtotal, 50);
  assert.equal(result.discountTotal, 0);
  assert.equal(result.tax, 9.5);
  assert.equal(result.total, 59.5);
});

test("priceOrder applies per-line volume discounts", () => {
  const result = priceOrder(tieredOrder);
  assert.equal(result.lines[0].discount, 187.5);
  assert.equal(result.lines[1].discount, 2.38);
  assert.equal(result.subtotal, 1297.5);
  assert.equal(result.discountTotal, 189.88);
});

test("priceOrder totals net plus tax", () => {
  const result = priceOrder(tieredOrder);
  assert.equal(result.net, 1107.62);
  assert.equal(result.tax, 221.52);
  assert.equal(result.total, 1329.14);
});

test("renderInvoice prints one row per line plus the totals block", () => {
  const invoice = renderInvoice(smallOrder);
  assert.equal(invoice.split("\n").length, 5);
  assert.match(invoice, /Standard seat x4 {2}50\.00 EUR/);
  assert.match(invoice, /Total 59\.50 EUR/);
});
