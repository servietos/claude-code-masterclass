const ledger = require("./ledger");

let nextNumber = 1000;

function create(customer, lines) {
  const number = nextNumber++;
  const total = lines.reduce((sum, line) => sum + line.quantity * line.price, 0);
  ledger.record({ account: customer, amount: total, type: "invoice", number });
  return { number, customer, lines, total };
}

// FIXME: nextNumber lives in memory, a restart reissues numbers already sent to customers
function peekNumber() {
  return nextNumber;
}

// TODO: show the tax split per line in the PDF layout
function describe(invoice) {
  return invoice.number + " | " + invoice.customer + " | " + invoice.total;
}

module.exports = { create, peekNumber, describe };
