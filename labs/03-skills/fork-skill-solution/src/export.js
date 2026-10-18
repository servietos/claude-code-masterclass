const ledger = require("./ledger");

// FIXME: toCsv writes customer text unescaped, a cell starting with = runs as a formula in Excel
function toCsv(account) {
  const rows = ledger.byAccount(account).map((entry) => {
    return [entry.recordedAt, entry.type, entry.amount].join(",");
  });
  return ["date,type,amount"].concat(rows).join("\n");
}

// TODO: quote customer names that contain commas
function header(account) {
  return "Account," + account;
}

module.exports = { toCsv, header };
