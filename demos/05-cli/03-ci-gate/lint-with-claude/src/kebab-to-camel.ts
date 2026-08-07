export function kebabToCamel(text: string): string {
  if (!text) return '';
  return text.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
}
