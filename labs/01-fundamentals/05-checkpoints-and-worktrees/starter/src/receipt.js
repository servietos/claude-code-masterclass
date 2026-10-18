export function renderReceipt(order) {
  const rows = order.lines.map(
    (line) => `${line.name} x${line.quantity}  ${line.total.toFixed(2)}`
  );
  const total = `Total ${order.total.toFixed(2)}`;
  return [...rows, total].join("\n");
}
