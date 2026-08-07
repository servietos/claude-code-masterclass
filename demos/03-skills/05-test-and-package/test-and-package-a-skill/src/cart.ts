export interface CartLine {
  sku: string;
  unitPrice: number;
  quantity: number;
}

export function lineTotal(line: CartLine): number {
  return line.unitPrice * line.quantity;
}

export function cartTotal(lines: CartLine[]): number {
  return lines.reduce((sum, line) => sum + lineTotal(line), 0);
}
