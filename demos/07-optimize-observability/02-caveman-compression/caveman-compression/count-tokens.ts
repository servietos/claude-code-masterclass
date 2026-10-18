import { readFileSync } from "fs"
import { getEncoding } from "js-tiktoken"

const file = process.argv[2] ?? "CLAUDE.verbose.md"
const text = readFileSync(file, "utf-8")

const enc = getEncoding("cl100k_base")
const tokens = enc.encode(text)

const count = tokens.length
console.log(`File:   ${file}`)
console.log(`Tokens: ${count}`)

if (count > 3000) {
  console.warn(`WARNING: token count exceeds 3000: consider compressing this file`)
}
