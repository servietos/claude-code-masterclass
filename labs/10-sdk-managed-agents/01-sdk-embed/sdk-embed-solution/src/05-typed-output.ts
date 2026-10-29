import { z } from "zod";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../.env", import.meta.url)), quiet: true });

const IncidentSchema = z.object({
  severity: z.enum(["P0", "P1", "P2", "P3"]),
  affected_services: z.array(z.string()),
  customer_facing: z.boolean(),
  eta_minutes_to_resolution: z.number().int().nullable(),
  one_line_summary: z.string(),
});

export type Incident = z.infer<typeof IncidentSchema>;

const report = `At 14:03 UTC the checkout-api started returning 503 for roughly 40 percent of requests.
The on-call engineer traced it to connection-pool exhaustion against the orders database after a
deploy raised the per-request query count. Payments and the mobile app are both affected because
they call checkout-api synchronously. A rollback is running now and should complete in about
twenty minutes. No data loss has been observed.`;

export function extractIncident(raw: string): Incident {
  const jsonText = raw.trim().replace(/^```(?:json)?\s*/i, "").replace(/```$/i, "");
  return IncidentSchema.parse(JSON.parse(jsonText));
}

const response = query({
  prompt: `Extract structured data from this incident report. Return ONLY a JSON object, no prose and no code fence, matching exactly this shape:
{"severity":"P0"|"P1"|"P2"|"P3","affected_services":string[],"customer_facing":boolean,"eta_minutes_to_resolution":number|null,"one_line_summary":string}

Incident report:
${report}`,
  options: {
    systemPrompt:
      "You are a data extraction service. You reply with a single JSON object and nothing else.",
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

const incident = extractIncident(text);
console.log(incident);
console.log(`severity: ${incident.severity}`);
console.log(`services: ${incident.affected_services.join(", ")}`);
