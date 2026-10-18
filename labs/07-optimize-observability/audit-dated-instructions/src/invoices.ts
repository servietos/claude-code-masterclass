export interface Invoice {
  customer: string;
  amountCents: number;
}

export function totalCents(invoices: Invoice[]): number {
  return invoices.reduce((sum, invoice) => sum + invoice.amountCents, 0);
}

export function applyDiscount(amountCents: number, percent: number): number {
  return Math.max(0, Math.round(amountCents * (1 - percent / 100)));
}
