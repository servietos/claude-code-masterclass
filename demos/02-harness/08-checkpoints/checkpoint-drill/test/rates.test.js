import test from "node:test";
import assert from "node:assert/strict";
import { discountFor, discountRate } from "../src/discount.js";
import { taxFor, taxRate } from "../src/tax.js";

test("discountRate picks the highest matching tier", () => {
  assert.equal(discountRate(4), 0);
  assert.equal(discountRate(10), 0.05);
  assert.equal(discountRate(50), 0.1);
  assert.equal(discountRate(120), 0.15);
});

test("discountFor applies the tier to the line total", () => {
  assert.equal(discountFor(100, 1250), 187.5);
  assert.equal(discountFor(4, 50), 0);
});

test("taxRate falls back to zero for unknown countries", () => {
  assert.equal(taxRate("AT"), 0.2);
  assert.equal(taxRate("DE"), 0.19);
  assert.equal(taxRate("XX"), 0);
});

test("taxFor applies the country rate to the net amount", () => {
  assert.equal(taxFor("AT", 1107.62), 221.52);
  assert.equal(taxFor("DE", 50), 9.5);
});
