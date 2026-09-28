import { describe, expect, it } from "vitest";
import { orderTotal } from "./orders";

describe("orderTotal", () => {
  it("sums quantity times unit price", () => {
    expect(orderTotal([{ sku: "A1", quantity: 2, unitPrice: 5 }, { sku: "B2", quantity: 1, unitPrice: 3 }])).toBe(13);
  });
});
