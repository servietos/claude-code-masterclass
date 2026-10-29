import { query, AbortError } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../.env", import.meta.url)), quiet: true });

const abortController = new AbortController();

process.on("SIGINT", () => {
  abortController.abort();
  process.stdout.write("\ninterrupted\n");
  // 130 is the conventional exit code for a process killed by Ctrl-C (128 plus SIGINT)
  process.exit(130);
});

async function main() {
  for await (const msg of query({
    prompt: "Explain how a B-tree index works. Be thorough.",
    options: {
      maxTurns: 1,
      abortController,
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.message.content) {
        if (block.type === "text") process.stdout.write(block.text);
      }
    }
  }
  process.stdout.write("\n");
}

main().catch((err) => {
  if (err instanceof AbortError) process.exit(130);
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
