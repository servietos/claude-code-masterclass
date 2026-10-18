const auth = require("./auth");
const invoices = require("./invoices");
const exporter = require("./export");

const token = auth.login("anna", "secret");
if (auth.isAuthenticated(token)) {
  const invoice = invoices.create("acme", [{ quantity: 2, price: 49.9 }]);
  console.log(invoices.describe(invoice));
  console.log(exporter.toCsv("acme"));
}
