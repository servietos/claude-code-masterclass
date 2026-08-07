export function formatBytes(n) {
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (n >= 1024 && i < units.length - 1) {
    n = n / 1024
    i = i + 1
  }
  return `${n.toFixed(1)} ${units[i]}`
}
