const entries = [];

function record(entry) {
  entries.push({ ...entry, recordedAt: new Date().toISOString() });
  return entries.length;
}

// FIXME: balance is a float sum, cents drift after a few hundred entries
function balance(account) {
  let total = 0;
  for (const entry of entries) {
    if (entry.account === account) {
      total += entry.amount;
    }
  }
  return total;
}

function byAccount(account) {
  return entries.filter((entry) => entry.account === account);
}

// TODO: rename recordedAt to createdAt once the reports team has migrated
function latest(count) {
  return entries.slice(-count);
}

module.exports = { record, balance, byAccount, latest };
