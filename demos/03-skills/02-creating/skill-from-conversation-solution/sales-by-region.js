function salesByRegion(records) {
  const totals = new Map();
  for (const { region, amount } of records) {
    totals.set(region, (totals.get(region) || 0) + amount);
  }
  return [...totals]
    .map(([region, total]) => ({ region, total }))
    .sort((a, b) => b.total - a.total);
}

function formatReport(results) {
  return results
    .map(({ region, total }) => `Region: ${region}  Revenue: $${total.toFixed(2)}`)
    .join('\n');
}

module.exports = { salesByRegion, formatReport };

if (require.main === module) {
  const records = [
    { region: 'East', product: 'Widget', amount: 1200.5 },
    { region: 'North', product: 'Gadget', amount: 1000 },
    { region: 'South', product: 'Gizmo', amount: 990.25 },
    { region: 'East', product: 'Gadget', amount: 850 },
    { region: 'North', product: 'Widget', amount: 646 },
    { region: 'South', product: 'Widget', amount: 1040.75 },
    { region: 'East', product: 'Gizmo', amount: 400 },
    { region: 'North', product: 'Gizmo', amount: 500 },
  ];
  console.log(formatReport(salesByRegion(records)));
}
