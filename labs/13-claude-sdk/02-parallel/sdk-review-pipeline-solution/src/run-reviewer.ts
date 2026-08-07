import { query } from "@anthropic-ai/claude-agent-sdk";
import { parseJsonBlock, type Review, type ReviewerConfig } from "./reviewers.js";

export type ReviewerRun = {
  reviewer: ReviewerConfig["name"];
  review: Review;
  costUsd: number;
  durationMs: number;
};

export async function runReviewer(
  config: ReviewerConfig,
  filePath: string,
  fileContents: string,
): Promise<ReviewerRun> {
  const startedAt = Date.now();

  const response = query({
    prompt:
      "Review the following file. Return ONLY JSON, no prose and no code fence, matching exactly this shape:\n" +
      '{"reviewer":"' +
      config.name +
      '","findings":[{"line":number|null,"severity":"critical"|"high"|"medium"|"low","summary":string,"recommendation":string}],"overall_verdict":"block"|"comment"|"approve"}' +
      "\n\n<file path='" +
      filePath +
      "'>\n" +
      fileContents +
      "\n</file>",
    options: {
      systemPrompt: config.systemPrompt,
      tools: [],
    },
  });

  let text = "";
  let costUsd = 0;

  for await (const message of response) {
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "text") {
          text += block.text;
        }
      }
    }
    if (message.type === "result") {
      costUsd = message.total_cost_usd;
    }
  }

  const review = config.reviewerSchema.parse(parseJsonBlock(text)) as Review;

  return {
    reviewer: config.name,
    review,
    costUsd,
    durationMs: Date.now() - startedAt,
  };
}
