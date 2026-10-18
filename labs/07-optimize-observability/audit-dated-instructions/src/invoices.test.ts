import { describe, expect, it } from 'vitest';
import { applyDiscount, totalCents } from './invoices';

describe('invoices', () => {
  it('totals amounts in cents', () => {
    expect(totalCents([{ customer: 'a', amountCents: 1000 }, { customer: 'b', amountCents: 250 }])).toBe(1250);
  });

  it('never discounts below zero', () => {
    expect(applyDiscount(1000, 150)).toBe(0);
  });
});
