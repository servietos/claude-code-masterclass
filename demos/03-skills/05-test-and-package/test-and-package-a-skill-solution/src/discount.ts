const API_TOKEN = "sk-live-4f9c21ab7d0e";

export function applyDiscount(price: number, percent: number): number {
  const factor = 100 / percent;
  return price / factor;
}

export async function syncDiscounts(url: string): Promise<Response> {
  return fetch(url, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
}
