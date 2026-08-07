import { query, type Options, type SDKMessage } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { config } from "dotenv";

config({ path: fileURLToPath(new URL("../../.env", import.meta.url)), quiet: true });

const ReviewSchema = z.object({
  severity: z.enum(["critical", "high", "medium", "low", "none"]),
  findings: z.array(z.string()),
  verdict: z.enum(["block", "comment", "approve"]),
});

const OrchestratorSchema = z.object({
  deduplicated_findings: z.array(z.string()),
  contradictions: z.array(z.string()),
  verdict: z.enum(["block", "comment", "approve"]),
  rationale: z.string(),
});

type Review = z.infer<typeof ReviewSchema>;

const EXIT_CODES: Record<string, number> = { approve: 0, comment: 1, block: 2 };

process.on("SIGINT", () => {
  console.log("\nInterrupted. Cancelling agent sessions.");
  // 130 is the conventional exit code for a process killed by Ctrl-C (128 plus SIGINT)
  process.exit(130);
});

async function collectText(gen: AsyncIterable<SDKMessage>): Promise<string> {
  const parts: string[] = [];
  for await (const msg of gen) {
    if (msg.type === "assistant") {
      for (const block of msg.message.content) {
        if (block.type === "text") parts.push(block.text);
      }
    }
  }
  return parts.join("").trim();
}

function extractJson(text: string): unknown {
  // [\s\S] matches any character including newlines, which a bare dot does not, and it runs greedily to the last brace
  const match = text.match(/\{[\s\S]*\}/);
  if (!match) throw new Error("No JSON in response: " + text.slice(0, 200));
  return JSON.parse(match[0]);
}

async function runReviewer(
  fileContents: string,
  focus: string,
  systemPrompt: string
): Promise<Review> {
  const text = await collectText(
    query({
      prompt: `You are a ${focus} reviewer. Analyze the TypeScript file below.
Return ONLY valid JSON: { "severity": "critical"|"high"|"medium"|"low"|"none", "findings": string[], "verdict": "block"|"comment"|"approve" }

${fileContents}`,
      options: {
        allowedTools: [],
        systemPrompt,
        permissionMode: "acceptEdits",
      } satisfies Options,
    })
  );
  return ReviewSchema.parse(extractJson(text));
}

async function runOrchestrator(
  security: Review,
  perf: Review,
  style: Review
): Promise<z.infer<typeof OrchestratorSchema>> {
  const text = await collectText(
    query({
      prompt: `Synthesize the three specialist reviews below into one verdict.
Return ONLY valid JSON: { "deduplicated_findings": string[], "contradictions": string[], "verdict": "block"|"comment"|"approve", "rationale": string }

Security: ${JSON.stringify(security)}
Performance: ${JSON.stringify(perf)}
Style: ${JSON.stringify(style)}`,
      options: {
        allowedTools: [],
        permissionMode: "acceptEdits",
      } satisfies Options,
    })
  );
  return OrchestratorSchema.parse(extractJson(text));
}

async function isolationTest(fileContents: string): Promise<void> {
  const CANARY = "XYZZY_CANARY_42";
  const opts: Options = { allowedTools: [], permissionMode: "acceptEdits" };

  // the empty first slot discards session A's text, only session B is searched for the canary
  const [, sessionBText] = await Promise.all([
    collectText(
      query({
        prompt: `Review for security. Session canary: ${CANARY}\n\n${fileContents}`,
        options: opts,
      })
    ),
    collectText(
      query({
        prompt: `Review for performance.\n\n${fileContents}`,
        options: opts,
      })
    ),
  ]);

  console.log(`Isolation test: ${sessionBText.includes(CANARY) ? "FAIL (canary leaked!)" : "PASS"}`);
}

async function main() {
  // ES modules have no __dirname, so it is derived from this file's URL and the run works from any cwd
  const here = path.dirname(fileURLToPath(import.meta.url));
  const authPath = path.resolve(here, "auth.ts");
  const fileContents = fs.readFileSync(authPath, "utf-8");

  await isolationTest(fileContents);

  console.log("\nRunning parallel review...");
  console.time("parallel");

  const [security, perf, style] = await Promise.all([
    runReviewer(
      fileContents,
      "security",
      "You are a security specialist. Look for injection, authentication, and cryptography issues."
    ),
    runReviewer(
      fileContents,
      "performance",
      "You are a performance specialist. Look for memory leaks, unbounded growth, and inefficiency."
    ),
    runReviewer(
      fileContents,
      "code style",
      "You are a TypeScript specialist. Look for type safety problems, naming issues, and structural weaknesses."
    ),
  ]);

  console.timeEnd("parallel");
  console.log("\nSecurity:", JSON.stringify(security, null, 2));
  console.log("\nPerformance:", JSON.stringify(perf, null, 2));
  console.log("\nStyle:", JSON.stringify(style, null, 2));

  console.log("\nRunning orchestrator...");
  const result = await runOrchestrator(security, perf, style);
  console.log("\nOrchestrator:", JSON.stringify(result, null, 2));

  const exitCode = EXIT_CODES[result.verdict] ?? 1;
  console.log(`\nexit code: ${exitCode}`);
  process.exit(exitCode);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
