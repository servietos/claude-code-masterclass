import { query, AbortError } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../.env", import.meta.url)), quiet: true });

const AuditSchema = z.object({
  severity: z.enum(["none", "low", "medium", "high", "critical"]),
  findings: z.array(z.string()),
  verdict: z.enum(["pass", "comment", "block"]),
});

const EXIT_CODES: Record<string, number> = { pass: 0, comment: 1, block: 2 };

const abortController = new AbortController();

process.on("SIGINT", () => {
  abortController.abort();
  console.error("interrupted");
  // 130 is the conventional exit code for a process killed by Ctrl-C (128 plus SIGINT)
  process.exit(130);
});

async function main() {
  const pkgPath = path.resolve(process.argv[2] ?? "package.json");
  const pkgContent = fs.readFileSync(pkgPath, "utf-8");

  const parts: string[] = [];

  for await (const msg of query({
    prompt: `Audit this package.json for missing required fields (name, version, description, license).
Return ONLY valid JSON matching this schema exactly:
{ "severity": "none"|"low"|"medium"|"high"|"critical", "findings": string[], "verdict": "pass"|"comment"|"block" }

${pkgContent}`,
    options: {
      tools: [],
      allowedTools: [],
      permissionMode: "acceptEdits",
      maxTurns: 1,
      abortController,
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.message.content) {
        if (block.type === "text") parts.push(block.text);
      }
    }
  }

  const raw = parts.join("").trim();
  // [\s\S] matches any character including newlines, which a bare dot does not, and it runs greedily to the last brace
  const match = raw.match(/\{[\s\S]*\}/);
  if (!match) throw new Error("No JSON found in response");

  const result = AuditSchema.parse(JSON.parse(match[0]));
  console.log(JSON.stringify(result, null, 2));
  process.exit(EXIT_CODES[result.verdict] ?? 1);
}

main().catch((err) => {
  if (err instanceof AbortError) process.exit(130);
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
