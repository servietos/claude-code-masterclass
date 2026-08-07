export function kebabToCamel(text: string): string {
  if (!text) return '';
  return text.replace(/-+([a-z0-9])/gi, (_, char: string) => char.toUpperCase());
}
