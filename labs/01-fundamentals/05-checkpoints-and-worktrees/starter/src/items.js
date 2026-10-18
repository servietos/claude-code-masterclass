export const ITEMS = [
  { sku: "tea", name: "Green tea", price: 3.5 },
  { sku: "mug", name: "Ceramic mug", price: 8 },
  { sku: "honey", name: "Honey jar", price: 6.25 }
];

export function findItem(sku) {
  return ITEMS.find((item) => item.sku === sku) ?? null;
}
