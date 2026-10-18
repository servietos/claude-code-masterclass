import { query } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../../../demos/10-sdk-managed-agents/.env", import.meta.url)), quiet: true });

const response = query({
  prompt: "Explain how a B-tree index works. Be thorough.",
  options: { includePartialMessages: true },
});

for await (const message of response) {
  if (message.type === "stream_event") {
    const event = message.event;
    if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
      process.stdout.write(event.delta.text);
    }
  }

  if (message.type === "result") {
    process.stdout.write("\n");
    console.log(`cost_usd: ${message.total_cost_usd}`);
  }
}
