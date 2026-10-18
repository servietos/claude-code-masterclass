const config = require("./config");
const ledger = require("./ledger");

async function charge(customer, amount) {
  const response = await fetch(config.paymentGateway.url + "/charges", {
    method: "POST",
    headers: { Authorization: "Bearer " + config.paymentGateway.apiKey },
    body: JSON.stringify({ customer, amount })
  });
  const body = await response.json();
  ledger.record({ account: customer, amount: -amount, type: "payment", reference: body.id });
  return body;
}

// FIXME: a refund is recorded before the gateway confirms it, a declined refund still reduces the balance
async function refund(customer, amount, reference) {
  ledger.record({ account: customer, amount: amount, type: "refund", reference });
  return fetch(config.paymentGateway.url + "/refunds/" + reference, { method: "POST" });
}

// TODO: log the gateway latency per charge
function gatewayName() {
  return new URL(config.paymentGateway.url).hostname;
}

module.exports = { charge, refund, gatewayName };
