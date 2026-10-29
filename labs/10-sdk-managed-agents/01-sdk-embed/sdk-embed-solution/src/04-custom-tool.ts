import { z } from "zod";
import { createSdkMcpServer, query, tool } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../.env", import.meta.url)), quiet: true });

const currentWeather = tool(
  "current_weather",
  "Returns the current weather for a given city.",
  { city: z.string().describe("City name, for example Berlin") },
  async ({ city }) => ({
    content: [
      {
        type: "text" as const,
        text: JSON.stringify({
          city,
          temperature_c: 18,
          conditions: "cloudy",
          humidity: 0.62,
        }),
      },
    ],
  }),
);

const weatherServer = createSdkMcpServer({
  name: "weather",
  version: "1.0.0",
  tools: [currentWeather],
});

const response = query({
  prompt:
    "Should I pack a jacket if I'm flying to Berlin tomorrow morning? And to Madrid? Use the current_weather tool.",
  options: {
    mcpServers: { weather: weatherServer },
    allowedTools: ["mcp__weather__current_weather"],
    tools: [],
  },
});

for await (const message of response) {
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "text") {
        console.log(block.text);
      }
      if (block.type === "tool_use") {
        console.log(`[tool_use] ${block.name} ${JSON.stringify(block.input)}`);
      }
    }
  }

  if (message.type === "user" && Array.isArray(message.message.content)) {
    for (const block of message.message.content) {
      if (block.type === "tool_result") {
        console.log(`[tool_result] ${JSON.stringify(block.content)}`);
      }
    }
  }

  if (message.type === "result") {
    console.log(`cost_usd: ${message.total_cost_usd}`);
  }
}
