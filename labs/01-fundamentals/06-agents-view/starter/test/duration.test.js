import test from "node:test";
import assert from "node:assert/strict";
import { parseDuration } from "../src/duration.js";

test("parseDuration reads seconds, minutes and hours", () => {
  assert.equal(parseDuration("30s"), 30);
  assert.equal(parseDuration("5m"), 300);
  assert.equal(parseDuration("2h"), 7200);
});

test("parseDuration reads a bare number as seconds", () => {
  assert.equal(parseDuration("90"), 90);
});

test("parseDuration rejects text that is not a duration", () => {
  assert.throws(() => parseDuration("soon"), /Invalid duration/);
});
