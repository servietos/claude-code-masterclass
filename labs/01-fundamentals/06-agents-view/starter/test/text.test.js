import test from "node:test";
import assert from "node:assert/strict";
import { slugify, truncate } from "../src/text.js";

test("slugify lowercases and joins words with hyphens", () => {
  assert.equal(slugify("Hello World"), "hello-world");
});

test("slugify drops leading and trailing separators", () => {
  assert.equal(slugify("  --Agents View--  "), "agents-view");
});

test("truncate leaves short text alone", () => {
  assert.equal(truncate("short", 10), "short");
});

test("truncate cuts long text and adds an ellipsis", () => {
  assert.equal(truncate("background session", 11), "background…");
});
