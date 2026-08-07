import { readFileSync } from "node:fs";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../../../demos/13-claude-sdk/.env", import.meta.url)), quiet: true });

const sessionId = readFileSync(".session-id.txt", "utf8").trim();

const response = query({
  prompt: "What changes if writes go up to 5k/sec?",
  options: { resume: sessionId, includePartialMessages: true },
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
    console.log(`resumed session: ${message.session_id}`);
  }
}
