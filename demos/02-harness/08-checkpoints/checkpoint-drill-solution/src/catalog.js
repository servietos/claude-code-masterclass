const CATALOG = {
  "seat-standard": { name: "Standard seat", unitPrice: 12.5 },
  "seat-pro": { name: "Pro seat", unitPrice: 29.0 },
  "support-gold": { name: "Gold support", unitPrice: 199.99 },
  "storage-block": { name: "Storage block 100 GB", unitPrice: 4.75 }
};

export function findProduct(sku) {
  return CATALOG[sku] ?? null;
}

export function listSkus() {
  return Object.keys(CATALOG);
}
