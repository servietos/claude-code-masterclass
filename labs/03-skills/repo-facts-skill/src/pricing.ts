export function lineTotal(unitPriceCents: number, quantity: number): number {
  return unitPriceCents * quantity;
}

export function applyDiscount(totalCents: number, percent: number): number {
  return totalCents - (totalCents * percent) / 100;
}
