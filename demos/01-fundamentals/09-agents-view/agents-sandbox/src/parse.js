export function parseDuration(text) {
  const match = text.match(/^(\d+)(s|m|h)$/)
  const units = { s: 1, m: 60, h: 3600 }
  return Number(match[1]) * units[match[2]]
}
