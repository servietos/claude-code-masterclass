/**
 * Converts a kebab-case string into camelCase.
 *
 * @param input - The kebab-case text to convert.
 * @returns The input with every hyphen removed and the first letter of each
 * segment after the first upper-cased.
 */
export function kebabToCamel(input: string): string {
  return input
    .split('-')
    .filter((segment) => segment.length > 0)
    .map((segment, index) =>
      index === 0 ? segment : segment.charAt(0).toUpperCase() + segment.slice(1)
    )
    .join('');
}
