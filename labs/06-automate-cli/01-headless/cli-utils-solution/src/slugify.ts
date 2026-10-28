/**
 * Converts arbitrary text into a URL-safe slug.
 *
 * @param input - The raw text to convert.
 * @returns The lowercased text with every run of non-alphanumerics replaced by a
 * single hyphen and leading and trailing hyphens removed.
 */
export function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
