const { priceOrder } = require('./orders');

const ORDERS = [
  {
    id: 'A-1001',
    customer: 'Northwind',
    lines: [
      { sku: 'KEY-01', quantity: 2, unitPrice: 49.5 },
      { sku: 'MSE-04', quantity: 1, unitPrice: 24.0 }
    ]
  },
  {
    id: 'A-1002',
    customer: 'Contoso',
    lines: [
      { sku: 'MON-27', quantity: 3, unitPrice: 189.0 },
      { sku: 'CAB-02', quantity: 4, unitPrice: 12.5 }
    ]
  },
  {
    id: 'A-1003',
    customer: 'Fabrikam',
    lines: [{ sku: 'PEN-11', quantity: 6, unitPrice: 3.75 }]
  }
];

function formatReport(priced) {
  return priced
    .map((o) => `${o.id}  ${o.customer.padEnd(10)} net $${o.net.toFixed(2)}  total $${o.total.toFixed(2)}`)
    .join('\n');
}

if (require.main === module) {
  console.log(formatReport(ORDERS.map(priceOrder)));
}

module.exports = { ORDERS, formatReport };
