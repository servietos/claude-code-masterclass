export interface OrderLine {
  sku: string;
  quantity: number;
  unitPrice: number;
}

export function orderTotal(lines: OrderLine[]): number {
  return lines.reduce((sum, line) => sum + line.quantity * line.unitPrice, 0);
}
