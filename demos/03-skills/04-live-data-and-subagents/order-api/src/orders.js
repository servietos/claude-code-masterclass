const { applyPricing } = require('./pricing');

function lineTotal(line) {
  return line.quantity * line.unitPrice;
}

// TODO: reject orders with duplicate SKUs instead of silently summing them
function subtotalOf(order) {
  return order.lines.reduce((sum, line) => sum + lineTotal(line), 0);
}

function priceOrder(order) {
  const pricing = applyPricing(subtotalOf(order));
  return { id: order.id, customer: order.customer, ...pricing };
}

module.exports = { lineTotal, subtotalOf, priceOrder };
