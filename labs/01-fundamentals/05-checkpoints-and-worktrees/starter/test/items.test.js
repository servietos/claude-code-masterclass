import test from "node:test";
import assert from "node:assert/strict";
import { findItem, ITEMS } from "../src/items.js";

test("findItem returns the item with its price", () => {
  assert.deepEqual(findItem("mug"), { sku: "mug", name: "Ceramic mug", price: 8 });
});

test("findItem returns null for an unknown sku", () => {
  assert.equal(findItem("kettle"), null);
});

test("the catalog lists three items", () => {
  assert.equal(ITEMS.length, 3);
});
