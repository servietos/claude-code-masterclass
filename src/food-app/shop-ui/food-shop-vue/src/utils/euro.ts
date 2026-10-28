export function toEuro(value: number | null | undefined): string {
  return `${value?.toFixed(2)} €`;
}
