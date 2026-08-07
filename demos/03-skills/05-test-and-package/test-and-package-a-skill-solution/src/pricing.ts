import { CartLine, cartTotal } from "./cart.js";

export interface Quote {
  subtotal: number;
  currency: string;
}

export function quote(lines: CartLine[], currency = "EUR"): Quote {
  return { subtotal: cartTotal(lines), currency };
}
