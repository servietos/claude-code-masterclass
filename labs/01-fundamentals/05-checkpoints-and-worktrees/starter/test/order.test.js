import test from "node:test";
import assert from "node:assert/strict";
import { buildOrder } from "../src/order.js";

const entries = [
  { sku: "tea", quantity: 2 },
  { sku: "mug", quantity: 1 },
  { sku: "honey", quantity: 1 }
];

test("buildOrder prices every line", () => {
  const order = buildOrder(entries);
  assert.equal(order.lines.length, 3);
  assert.equal(order.lines[0].total, 7);
  assert.equal(order.lines[2].total, 6.25);
});

test("buildOrder totals the order", () => {
  assert.equal(buildOrder(entries).total, 21.25);
});
