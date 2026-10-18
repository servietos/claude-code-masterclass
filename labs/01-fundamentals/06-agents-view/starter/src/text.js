export function slugify(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function truncate(text, max) {
  if (text.length <= max) {
    return text;
  }
  return text.slice(0, max - 1) + "…";
}
