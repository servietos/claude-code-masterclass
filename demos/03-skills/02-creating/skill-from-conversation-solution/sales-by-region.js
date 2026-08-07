function salesByRegion(records) {
  const totals = new Map();
  for (const record of records) {
    const region = record.region;
    const amount = Number(record.amount) || 0;
    totals.set(region, (totals.get(region) || 0) + amount);
  }
  return [...totals.entries()]
    .map(([region, total]) => ({ region, total }))
    .sort((a, b) => b.total - a.total);
}

function formatReport(results) {
  return results
    .map((entry) => `Region: ${entry.region}  Revenue: $${entry.total.toFixed(2)}`)
    .join('\n');
}

module.exports = { salesByRegion, formatReport };

const sampleRecords = [
  { region: 'North', product: 'Widget', amount: 1200 },
  { region: 'North', product: 'Gadget', amount: 800.5 },
  { region: 'South', product: 'Widget', amount: 430.25 },
  { region: 'South', product: 'Sprocket', amount: 990 },
  { region: 'South', product: 'Gadget', amount: 610.75 },
  { region: 'East', product: 'Widget', amount: 2100 },
  { region: 'East', product: 'Sprocket', amount: 350 },
  { region: 'North', product: 'Sprocket', amount: 145.5 }
];

if (require.main === module) {
  const results = salesByRegion(sampleRecords);
  console.log(formatReport(results));
}
