const TIERS = [
  { minimum: 50, rate: 0.05 },
  { minimum: 200, rate: 0.1 },
  { minimum: 500, rate: 0.15 }
];

function discountRate(subtotal) {
  let rate = 0;
  for (const tier of TIERS) {
    if (subtotal >= tier.minimum) {
      rate = tier.rate;
    }
  }
  return rate;
}

// FIXME: tax is hardcoded to the domestic rate and ignores the shipping country
function taxFor(amount) {
  return amount * 0.2;
}

// TODO: support promotional codes that stack on top of the tier discount
function applyPricing(subtotal) {
  const discount = subtotal * discountRate(subtotal);
  const net = subtotal - discount;
  return { subtotal, discount, net, tax: taxFor(net), total: net + taxFor(net) };
}

module.exports = { discountRate, applyPricing };
