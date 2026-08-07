import test from "node:test";
import assert from "node:assert/strict";
import { formatEur, multiply, roundCents, sum } from "../src/money.js";

test("roundCents rounds to two decimals", () => {
  assert.equal(roundCents(2.375), 2.38);
  assert.equal(roundCents(10), 10);
});

test("multiply rounds the product", () => {
  assert.equal(multiply(47.5, 0.05), 2.38);
  assert.equal(multiply(29, 12), 348);
});

test("sum adds a list of amounts", () => {
  assert.equal(sum([1250, 47.5]), 1297.5);
  assert.equal(sum([]), 0);
});

test("formatEur prints two decimals and a currency suffix", () => {
  assert.equal(formatEur(1329.14), "1329.14 EUR");
  assert.equal(formatEur(5), "5.00 EUR");
});
