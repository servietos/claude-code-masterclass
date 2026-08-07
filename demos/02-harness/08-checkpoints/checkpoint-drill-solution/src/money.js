export function roundCents(amount) {
  return Math.round((amount + Number.EPSILON) * 100) / 100;
}

export function multiply(amount, factor) {
  return roundCents(amount * factor);
}

export function sum(amounts) {
  return roundCents(amounts.reduce((total, amount) => total + amount, 0));
}

export function formatEur(amount) {
  return `${roundCents(amount).toFixed(2)} EUR`;
}
