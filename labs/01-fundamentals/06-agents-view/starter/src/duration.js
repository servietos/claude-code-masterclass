const UNITS = { s: 1, m: 60, h: 3600 };

export function parseDuration(text) {
  const match = /^(\d+)(s|m|h)?$/.exec(text);
  if (!match) {
    throw new Error(`Invalid duration: ${text}`);
  }
  return Number(match[1]) * UNITS[match[2] ?? "s"];
}
