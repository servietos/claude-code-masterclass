const { spawn } = require("node:child_process");

const child = spawn("npx", ["-y", "@modelcontextprotocol/server-memory"], {
  shell: true,
  stdio: ["pipe", "pipe", "pipe"],
  env: { ...process.env, MEMORY_FILE_PATH: process.argv[2] || "" },
});

let buffer = "";
const seen = [];

child.stdout.on("data", (chunk) => {
  buffer += chunk.toString();
  let index;
  while ((index = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, index).trim();
    buffer = buffer.slice(index + 1);
    if (!line) continue;
    seen.push(line);
    console.log("RECV " + line);
  }
});

child.stderr.on("data", (chunk) => process.stderr.write("ERR " + chunk.toString()));

function send(obj) {
  child.stdin.write(JSON.stringify(obj) + "\n");
}

setTimeout(() => {
  send({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: "lab-probe", version: "1.0.0" },
    },
  });
}, 1500);

setTimeout(() => {
  send({ jsonrpc: "2.0", method: "notifications/initialized" });
  send({ jsonrpc: "2.0", id: 2, method: "tools/list" });
}, 4000);

setTimeout(() => {
  send({
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: {
      name: "create_entities",
      arguments: {
        entities: [
          {
            name: "Priya Raghunathan",
            entityType: "person",
            observations: ["Owns alert routing", "Weekly primary on-call handover Tuesdays 10:00 CET"],
          },
        ],
      },
    },
  });
}, 6000);

setTimeout(() => {
  send({ jsonrpc: "2.0", id: 4, method: "tools/call", params: { name: "read_graph", arguments: {} } });
}, 8000);

setTimeout(() => {
  child.kill();
  console.log("LINES " + seen.length);
  process.exit(0);
}, 11000);
