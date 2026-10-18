export function lineTotal(price, quantity) {
  return Math.round(price * quantity * 100) / 100;
}

export function orderTotal(lines) {
  const total = lines.reduce((running, line) => running + line.total, 0);
  return Math.round(total * 100) / 100;
}
