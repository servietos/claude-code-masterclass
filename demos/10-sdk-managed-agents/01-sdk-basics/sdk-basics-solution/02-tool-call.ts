import { query, tool, createSdkMcpServer, AbortError } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../.env", import.meta.url)), quiet: true });

const FORECASTS: Record<string, string> = {
  berlin: "8 C, light rain, wind 22 km/h",
  madrid: "24 C, sunny, wind 6 km/h",
};

const currentWeather = tool(
  "current_weather",
  "Returns current weather for a city.",
  { city: z.string().describe("City name, for example Berlin") },
  async ({ city }) => {
    const reading = FORECASTS[city.toLowerCase()] ?? "no data for this city";
    console.log(`[tool] current_weather(${city}) -> ${reading}`);
    return { content: [{ type: "text", text: reading }] };
  },
);

const weatherServer = createSdkMcpServer({
  name: "weather",
  version: "1.0.0",
  tools: [currentWeather],
});

const abortController = new AbortController();

process.on("SIGINT", () => {
  abortController.abort();
  process.stdout.write("\ninterrupted\n");
  // 130 is the conventional exit code for a process killed by Ctrl-C (128 plus SIGINT)
  process.exit(130);
});

async function main() {
  for await (const msg of query({
    prompt:
      "Should I pack a jacket if I'm flying to Berlin and Madrid tomorrow? Use the current_weather tool for each city.",
    options: {
      tools: [],
      mcpServers: { weather: weatherServer },
      allowedTools: ["mcp__weather__current_weather"],
      permissionMode: "acceptEdits",
      maxTurns: 6,
      abortController,
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.message.content) {
        if (block.type === "text") process.stdout.write(block.text);
        if (block.type === "tool_use") console.log(`[tool_use] ${block.name} ${JSON.stringify(block.input)}`);
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
