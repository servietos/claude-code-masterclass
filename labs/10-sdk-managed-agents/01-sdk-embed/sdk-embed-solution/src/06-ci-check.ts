import { readFileSync } from "node:fs";
import { z } from "zod";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../.env", import.meta.url)), quiet: true });

const AuditSchema = z.object({
  issues: z.array(z.string()),
  severity: z.enum(["pass", "warn", "fail"]),
});

export type Audit = z.infer<typeof AuditSchema>;

export const EXIT_CODES: Record<Audit["severity"], number> = {
  pass: 0,
  warn: 1,
  fail: 2,
};

export function parseAudit(raw: string): Audit {
  const jsonText = raw.trim().replace(/^```(?:json)?\s*/i, "").replace(/```$/i, "");
  return AuditSchema.parse(JSON.parse(jsonText));
}

export async function runAudit(packageJson: string): Promise<Audit> {
  const response = query({
    prompt: `Audit this package.json for issues. Return ONLY JSON: { issues: string[], severity: 'pass' | 'warn' | 'fail' }. Issues to flag: unused dependencies (best-effort), missing description, missing license, very old dependency versions, missing engines field.

${packageJson}`,
    options: {
      systemPrompt:
        "You are a package.json auditor. You reply with a single JSON object and nothing else.",
      tools: [],
    },
  });

  let text = "";
  for await (const message of response) {
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "text") {
          text += block.text;
        }
      }
    }
  }

  return parseAudit(text);
}

const packageJson = readFileSync("package.json", "utf8");
const audit = await runAudit(packageJson);

for (const issue of audit.issues) {
  console.log(`- ${issue}`);
}
console.log(`severity: ${audit.severity}`);

process.exit(EXIT_CODES[audit.severity]);
