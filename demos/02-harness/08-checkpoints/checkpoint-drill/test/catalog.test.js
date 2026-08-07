import test from "node:test";
import assert from "node:assert/strict";
import { findProduct, listSkus } from "../src/catalog.js";

test("findProduct returns a product with a unit price", () => {
  assert.deepEqual(findProduct("seat-pro"), { name: "Pro seat", unitPrice: 29.0 });
});

test("findProduct returns null for an unknown sku", () => {
  assert.equal(findProduct("seat-platinum"), null);
});

test("listSkus returns every catalog key", () => {
  assert.deepEqual(listSkus(), [
    "seat-standard",
    "seat-pro",
    "support-gold",
    "storage-block"
  ]);
});
