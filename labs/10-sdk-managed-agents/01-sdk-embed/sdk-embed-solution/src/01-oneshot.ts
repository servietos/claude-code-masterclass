import { query } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../.env", import.meta.url)), quiet: true });

const response = query({
  prompt:
    "What's the most important habit for an engineer to develop in their first year? Answer in three short bullets.",
});

for await (const message of response) {
  console.log(`[${message.type}]`);

  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "text") {
        console.log(block.text);
      }
    }
  }

  if (message.type === "result") {
    console.log(`cost_usd: ${message.total_cost_usd}`);
    console.log(`input_tokens: ${message.usage.input_tokens}`);
    console.log(`output_tokens: ${message.usage.output_tokens}`);
  }
}
