import test from "node:test";
import assert from "node:assert/strict";
import { buildOrder } from "../src/order.js";
import { renderReceipt } from "../src/receipt.js";

const order = buildOrder([
  { sku: "tea", quantity: 2 },
  { sku: "mug", quantity: 1 }
]);

test("renderReceipt prints one row per line", () => {
  const receipt = renderReceipt(order);
  assert.match(receipt, /Green tea x2 {2}7\.00/);
  assert.match(receipt, /Ceramic mug x1 {2}8\.00/);
});

test("renderReceipt prints the order total", () => {
  assert.match(renderReceipt(order), /total.*15\.00/i);
});
