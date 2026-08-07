const REVIEWS = {
  security: {
    reviewer: "security",
    findings: [
      {
        line: 14,
        severity: "critical",
        summary: "SQL injection via string-concatenated email in loginUser.",
        recommendation: "Use a parameterised query.",
      },
      {
        line: 8,
        severity: "high",
        summary: "MD5 with a hardcoded static salt for password hashing.",
        recommendation: "Use bcrypt, scrypt or argon2 with a per-user salt.",
      },
    ],
    overall_verdict: "block",
  },
  performance: {
    reviewer: "performance",
    findings: [
      {
        line: 3,
        severity: "medium",
        summary: "Module-level cache grows without bound, one entry per distinct password.",
        recommendation: "Drop the cache or bound it with an LRU.",
      },
    ],
    overall_verdict: "comment",
  },
  style: {
    reviewer: "style",
    findings: [
      {
        line: 13,
        severity: "medium",
        summary: "db parameter is typed any, defeating type safety.",
        recommendation: "Introduce a narrow Db interface.",
      },
      {
        line: 20,
        severity: "high",
        summary: "validateSession only checks token length.",
        recommendation: "Verify a signature and expiry.",
      },
    ],
    overall_verdict: "block",
  },
};

const ORCHESTRATION = {
  block: {
    deduplicated_findings: [
      {
        line: 14,
        severity: "critical",
        summary: "SQL injection in loginUser.",
        recommendation: "Use a parameterised query.",
        found_by: ["security"],
      },
      {
        line: 8,
        severity: "high",
        summary: "MD5 plus static salt for password hashing.",
        recommendation: "Use argon2.",
        found_by: ["security", "style"],
      },
    ],
    contradictions: [],
    verdict: "block",
    rationale: "A critical injection finding blocks the change.",
  },
  comment: {
    deduplicated_findings: [],
    contradictions: [],
    verdict: "comment",
    rationale: "Only medium findings.",
  },
  approve: {
    deduplicated_findings: [],
    contradictions: [],
    verdict: "approve",
    rationale: "No findings.",
  },
};

const SESSION_PREFIX = "aaaaaaaa-bbbb-cccc-dddd-";
let counter = 0;

function pickReviewer(systemPrompt) {
  if (systemPrompt.startsWith("You are a security")) return "security";
  if (systemPrompt.startsWith("You are a performance")) return "performance";
  if (systemPrompt.startsWith("You are a code-style")) return "style";
  return null;
}

export function tool(name, description, inputSchema, handler) {
  return { name, description, inputSchema, handler };
}

export function createSdkMcpServer(options) {
  return { type: "sdk", name: options.name, tools: options.tools ?? [] };
}

export function query({ prompt, options = {} }) {
  counter += 1;
  const sessionId = SESSION_PREFIX + String(counter).padStart(12, "0");
  const systemPrompt = typeof options.systemPrompt === "string" ? options.systemPrompt : "";
  const reviewerName = pickReviewer(systemPrompt);
  const delayMs = Number(process.env.STUB_DELAY_MS ?? "300");

  let payload;
  if (reviewerName) {
    payload = JSON.stringify(REVIEWS[reviewerName]);
    if (process.env.STUB_LEAK === "1" && reviewerName === "performance") {
      const leaked = structuredClone(REVIEWS.performance);
      leaked.findings[0].summary += " foxglove";
      payload = JSON.stringify(leaked);
    }
  } else {
    payload = JSON.stringify(ORCHESTRATION[process.env.STUB_VERDICT ?? "block"]);
  }

  return (async function* () {
    yield { type: "system", subtype: "init", uuid: "s", session_id: sessionId, tools: [], model: "stub" };
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    yield {
      type: "assistant",
      uuid: "a",
      session_id: sessionId,
      parent_tool_use_id: null,
      message: { role: "assistant", content: [{ type: "text", text: payload }] },
    };
    yield {
      type: "result",
      subtype: "success",
      duration_ms: delayMs,
      duration_api_ms: delayMs,
      is_error: false,
      num_turns: 1,
      result: "ok",
      stop_reason: "end_turn",
      total_cost_usd: 0.0031,
      usage: { input_tokens: 800, output_tokens: 200 },
      modelUsage: {},
      permission_denials: [],
      uuid: "r",
      session_id: sessionId,
    };
  })();
}
