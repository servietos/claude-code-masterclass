const SESSION_ID = "11111111-2222-3333-4444-555555555555";

const scenario = process.env.STUB_SCENARIO ?? "text";

export function tool(name, description, inputSchema, handler) {
  return { name, description, inputSchema, handler };
}

export function createSdkMcpServer(options) {
  return { type: "sdk", name: options.name, tools: options.tools ?? [] };
}

function assistantText(text) {
  return {
    type: "assistant",
    uuid: "a-1",
    session_id: SESSION_ID,
    parent_tool_use_id: null,
    message: { role: "assistant", content: [{ type: "text", text }] },
  };
}

function resultMessage() {
  return {
    type: "result",
    subtype: "success",
    duration_ms: 10,
    duration_api_ms: 8,
    is_error: false,
    num_turns: 1,
    result: "ok",
    stop_reason: "end_turn",
    total_cost_usd: 0.0042,
    usage: { input_tokens: 123, output_tokens: 45 },
    modelUsage: {},
    permission_denials: [],
    uuid: "r-1",
    session_id: SESSION_ID,
  };
}

const PAYLOADS = {
  text: "- Read code before writing code\n- Ask early\n- Write the test first",
  incident: JSON.stringify({
    severity: "P1",
    affected_services: ["checkout-api", "payments", "mobile-app"],
    customer_facing: true,
    eta_minutes_to_resolution: 20,
    one_line_summary: "Connection-pool exhaustion in checkout-api returns 503s.",
  }),
  audit_pass: JSON.stringify({ issues: [], severity: "pass" }),
  audit_warn: JSON.stringify({ issues: ["missing description"], severity: "warn" }),
  audit_fail: JSON.stringify({ issues: ["missing license", "missing engines"], severity: "fail" }),
  fenced: "```json\n" + JSON.stringify({ issues: ["missing description"], severity: "warn" }) + "\n```",
};

export function query({ prompt, options = {} }) {
  return (async function* () {
    yield {
      type: "system",
      subtype: "init",
      uuid: "s-1",
      session_id: SESSION_ID,
      tools: [],
      model: "stub",
    };

    if (options.includePartialMessages) {
      for (const chunk of ["A B-tree ", "keeps keys ", "sorted."]) {
        yield {
          type: "stream_event",
          uuid: "p-1",
          session_id: SESSION_ID,
          parent_tool_use_id: null,
          event: {
            type: "content_block_delta",
            index: 0,
            delta: { type: "text_delta", text: chunk },
          },
        };
      }
    }

    const servers = options.mcpServers ?? {};
    for (const [serverName, server] of Object.entries(servers)) {
      for (const city of ["Berlin", "Madrid"]) {
        const def = server.tools.find((t) => t.name === "current_weather");
        yield {
          type: "assistant",
          uuid: "a-t",
          session_id: SESSION_ID,
          parent_tool_use_id: null,
          message: {
            role: "assistant",
            content: [
              {
                type: "tool_use",
                id: `tu-${city}`,
                name: `mcp__${serverName}__${def.name}`,
                input: { city },
              },
            ],
          },
        };
        const out = await def.handler({ city }, {});
        yield {
          type: "user",
          uuid: "u-t",
          session_id: SESSION_ID,
          parent_tool_use_id: null,
          message: {
            role: "user",
            content: [{ type: "tool_result", tool_use_id: `tu-${city}`, content: out.content }],
          },
        };
      }
    }

    yield assistantText(PAYLOADS[scenario] ?? PAYLOADS.text);
    yield resultMessage();
  })();
}
