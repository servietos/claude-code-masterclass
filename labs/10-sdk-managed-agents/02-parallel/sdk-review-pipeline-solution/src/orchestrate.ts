import { z } from "zod";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { parseJsonBlock, type Review } from "./reviewers.js";

export const OrchestrationSchema = z.object({
  deduplicated_findings: z.array(
    z.object({
      line: z.number().int().nullable(),
      severity: z.enum(["critical", "high", "medium", "low"]),
      summary: z.string(),
      recommendation: z.string(),
      found_by: z.array(z.string()),
    }),
  ),
  contradictions: z.array(z.string()),
  verdict: z.enum(["block", "comment", "approve"]),
  rationale: z.string(),
});

export type Orchestration = z.infer<typeof OrchestrationSchema>;

export const ORCHESTRATOR_SYSTEM_PROMPT =
  "You are a code review orchestrator. Three reviewers have produced findings on a file. Your job is to (a) deduplicate findings that overlap across reviewers, (b) rank by severity, (c) issue a single overall verdict for the PR. Reviewers can be wrong, if one reviewer's finding is contradicted by another or seems mistaken, flag it. Return ONLY JSON.";

export const VERDICT_EXIT_CODES: Record<Orchestration["verdict"], number> = {
  approve: 0,
  comment: 1,
  block: 2,
};

export async function orchestrate(reviews: Review[]): Promise<Orchestration> {
  const response = query({
    prompt: `Here are the three reviewer reports:

${reviews.map((review) => JSON.stringify(review, null, 2)).join("\n\n")}

Return ONLY JSON matching:
{
  "deduplicated_findings": [{ "line": number|null, "severity": "critical"|"high"|"medium"|"low", "summary": string, "recommendation": string, "found_by": string[] }],
  "contradictions": string[],
  "verdict": "block"|"comment"|"approve",
  "rationale": string
}`,
    options: {
      systemPrompt: ORCHESTRATOR_SYSTEM_PROMPT,
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

  return OrchestrationSchema.parse(parseJsonBlock(text));
}

export function printSummary(result: Orchestration): void {
  console.log("Top findings:");
  for (const finding of result.deduplicated_findings.slice(0, 5)) {
    console.log(
      `  [${finding.severity}] line ${finding.line ?? "?"} ${finding.summary} (found_by: ${finding.found_by.join(", ")})`,
    );
  }

  if (result.contradictions.length > 0) {
    console.log("Contradictions:");
    for (const item of result.contradictions) {
      console.log(`  - ${item}`);
    }
  }

  console.log(`verdict: ${result.verdict}`);
  console.log(`rationale: ${result.rationale}`);
}
