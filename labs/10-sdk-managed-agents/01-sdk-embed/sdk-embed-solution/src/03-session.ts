import { writeFileSync } from "node:fs";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../.env", import.meta.url)), quiet: true });

const response = query({
  prompt:
    "I'm designing a URL shortener. The traffic profile is 10k reads/sec, 100 writes/sec. What storage would you start with?",
});

let sessionId = "";

for await (const message of response) {
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "text") {
        process.stdout.write(block.text);
      }
    }
  }

  if (message.type === "result") {
    sessionId = message.session_id;
  }
}

process.stdout.write("\n");
writeFileSync(".session-id.txt", sessionId, "utf8");
console.log(`session_id: ${sessionId}`);
