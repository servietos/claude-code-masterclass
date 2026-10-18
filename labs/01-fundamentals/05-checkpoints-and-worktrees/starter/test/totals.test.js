import test from "node:test";
import assert from "node:assert/strict";
import { lineTotal, orderTotal } from "../src/totals.js";

test("lineTotal multiplies price by quantity", () => {
  assert.equal(lineTotal(3.5, 2), 7);
  assert.equal(lineTotal(6.25, 3), 18.75);
});

test("lineTotal rounds to two decimals", () => {
  assert.equal(lineTotal(0.1, 3), 0.3);
});

test("orderTotal adds the line totals", () => {
  assert.equal(orderTotal([{ total: 7 }, { total: 8 }, { total: 6.25 }]), 21.25);
  assert.equal(orderTotal([]), 0);
});
