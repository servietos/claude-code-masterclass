import { multiply } from "./money.js";

const RATES = {
  AT: 0.2,
  DE: 0.19,
  CH: 0.081
};

export function taxRate(country) {
  return RATES[country] ?? 0;
}

export function taxFor(country, netAmount) {
  return multiply(netAmount, taxRate(country));
}
