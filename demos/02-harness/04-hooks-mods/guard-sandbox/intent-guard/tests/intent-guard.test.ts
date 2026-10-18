import { describe, expect, test } from "claude-code/testing";

const CWD = "D:\\work\\app";

function harness(on: any, answer: string | null | (() => Promise<string>)) {
  const asked: string[] = [];
  const ran: string[] = [];
  on("session.start", ($: any, e: any) => ({ cwd: e.cwd }));
  on("session.cwd", () => ({ value: CWD }));
  on("prompt.submit", ($: any, e: any) => ({ text: e.text }));
  on("turn.complete", () => ({ text: "" }));
  on("ui.open", () => ({ value: { isPlaced: true } }));
  on("ui.close", () => ({ value: {} }));
  on("tool.call", { tool: "AskUserQuestion" }, async ($: any, e: any) => {
    asked.push(e.questions?.[0]?.question ?? "");
    if (answer === null) return { deny: "no one to ask" };
    const label = typeof answer === "function" ? await answer() : answer;
    return { result: { questions: e.questions, answers: { [e.questions[0].question]: label } } };
  });
  for (const tool of ["Bash", "PowerShell"]) {
    on("tool.call", { tool }, ($: any, e: any) => {
      ran.push(e.command);
      return { result: { stdout: "ok", stderr: "", interrupted: false } };
    });
  }
  return { asked, ran };
}

async function start($: any) {
  await $.session.start({ surface: "terminal", isInteractive: true, cwd: CWD } as any);
}

async function say($: any, text: string, kind = "composer") {
  await $.prompt.submit({ text, wait: false, origin: { kind } } as any);
}

async function sh($: any, command: string, tool = "Bash") {
  return (await $.tool.call({ tool, command } as any)) as any;
}

describe("intent-guard", () => {
  test("restoring a database runs without asking when requested", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "download the green db and restore as dev db");
    const r = await sh($, `sqlcmd -S . -E -C -Q "RESTORE DATABASE [App-Dev] FROM DISK='x.bak' WITH REPLACE"`);
    expect(r.deny).toBeUndefined();
    expect(h.asked.length).toBe(0);
    expect(h.ran.length).toBe(1);
  });

  test("deleting a box and stopping containers runs when requested", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "can we stop old containers and delete the unused hetzner box");
    await sh($, "hcloud server delete old-box");
    await sh($, `ssh root@1.2.3.4 'cd /opt/app && docker compose down --remove-orphans'`);
    expect(h.asked.length).toBe(0);
    expect(h.ran.length).toBe(2);
  });

  test("an unrequested test run is held and Cancel denies it", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "income cannot be negative, fix the calculation");
    const r = await sh($, "npx vitest run src/app/vat");
    expect(h.asked.length).toBe(1);
    expect(h.ran.length).toBe(0);
    expect(String(r.deny ?? r.text)).toMatch(/Intent Guard/);
  });

  test("Proceed lets a held command run", async ($, on) => {
    const h = harness(on, "Proceed");
    await start($);
    await say($, "fix the rounding");
    await sh($, "git commit -m fix");
    expect(h.asked.length).toBe(1);
    expect(h.ran.length).toBe(1);
  });

  test("commit and push count only within the last messages", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "fix the rounding too and run the tests");
    await say($, "when complete commit and push");
    await sh($, "npx vitest run src/app/vat");
    await sh($, "git add -A && git commit -m fix && git push");
    expect(h.asked.length).toBe(0);
    await say($, "what is the status");
    await say($, "show me the page");
    await say($, "now fix the header");
    await sh($, "git commit -m again");
    expect(h.asked.length).toBe(1);
  });

  test("yes after a delete question counts as asking", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "replace the diagrams");
    await $.turn.complete({ reason: "answer", answer: "About the old diagrams: do you want them deleted?", durationMs: 1, isAborted: false, turnId: "t1" } as any);
    await say($, "yes");
    await sh($, "rm static/images/old.svg");
    expect(h.asked.length).toBe(0);
  });

  test("a peer session's words are not the user's", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "delete everything in assets", "peer");
    await sh($, "rm -rf assets");
    expect(h.asked.length).toBe(1);
  });

  test("a negated request does not count", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "fix it but do not push");
    await sh($, "git push origin master");
    expect(h.asked.length).toBe(1);
  });

  test("reads on boxes and databases and plain file work are never held", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "what model do we use on prod");
    await sh($, `ssh -i ~/.ssh/key root@1.2.3.4 'cat /opt/app/env/api-green.env'`);
    await sh($, `sqlcmd -S server -d app -Q "SELECT ModelName FROM AiModels"`, "PowerShell");
    await sh($, "sed -n 1,40p notes.md; cp a.txt b.txt; mv b.txt c.txt");
    expect(h.asked.length).toBe(0);
    expect(h.ran.length).toBe(3);
  });

  test("getting secrets from a secrets store is never held", async ($, on) => {
    const h = harness(on, "Cancel");
    const mcp: string[] = [];
    on("tool.call", { tool: "mcp__secrets-mcp__resolve_provider_key" }, () => (mcp.push("resolve"), { result: { value: "k" } }));
    on("tool.call", { tool: "mcp__secrets-mcp__render_app_env" }, () => (mcp.push("render"), { result: { value: "env" } }));
    await start($);
    await say($, "run the import with gpt-5.4-mini from foundry");
    await $.tool.call({ tool: "mcp__secrets-mcp__resolve_provider_key", provider: "deepseek", serviceKey: "chat" } as any);
    await $.tool.call({ tool: "mcp__secrets-mcp__render_app_env", app: "api" } as any);
    await sh($, `K=$(grep -E '^SECRETS_MCP_API_KEY=' .env | cut -d= -f2-); curl -s -H "X-API-Key: $K" https://store.example.com/api/ProviderKeys/resolve/ionos/chat`);
    await sh($, `python -c "import json;print(json.load(open('.mcp.json'))['mcpServers']['secrets-mcp']['headers'])"`);
    expect(h.asked.length).toBe(0);
    expect(mcp).toEqual(["resolve", "render"]);
    expect(h.ran.length).toBe(2);
  });

  test("an MCP delete is held unless asked", async ($, on) => {
    const h = harness(on, "Cancel");
    on("tool.call", { tool: "mcp__secrets-mcp__delete_provider_key" }, () => ({ result: { ok: true } }));
    await start($);
    await say($, "list the provider keys");
    const r: any = await $.tool.call({ tool: "mcp__secrets-mcp__delete_provider_key", provider: "deepseek" } as any);
    expect(h.asked.length).toBe(1);
    expect(String(r.deny ?? r.text)).toMatch(/Intent Guard/);
    await say($, "delete the deepseek key");
    await $.tool.call({ tool: "mcp__secrets-mcp__delete_provider_key", provider: "deepseek" } as any);
    expect(h.asked.length).toBe(1);
  });

  test("scratchpad cleanup and chrome-devtools restarts pass", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "check the page");
    await sh($, "rm -rf /c/Users/X/AppData/Local/Temp/claude/s/scratchpad/out");
    await sh($, "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'chrome-devtools-mcp' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }", "PowerShell");
    expect(h.asked.length).toBe(0);
  });

  test("full permissions covers database scripts and restarts", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "Override the blue and green db with dev so we can commit push pr full permissions");
    await sh($, "bash push-dev-to-box.sh --local-db app_dev --targets app,app-blue");
    await sh($, "taskkill //PID 5388 //F");
    expect(h.asked.length).toBe(0);
  });

  test("an unrequested database script is held", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "show me the settings page");
    await sh($, "bash apply-deltas.sh --slot green --delta db/deltas/2026-10-01.sql");
    expect(h.asked.length).toBe(1);
  });

  test("data writes run when requested", async ($, on) => {
    const h = harness(on, "Cancel");
    await start($);
    await say($, "set them as default in dev");
    await sh($, `sqlcmd -S localhost -d app -Q "UPDATE AiModels SET IsDefault=1 WHERE Name='gpt-oss-120b'"`);
    expect(h.asked.length).toBe(0);
  });

  test("with nobody to ask the held command is denied", async ($, on) => {
    const h = harness(on, null);
    await start($);
    await say($, "look at the logs");
    const r = await sh($, "git reset --hard HEAD");
    expect(h.ran.length).toBe(0);
    expect(String(r.deny ?? r.text)).toMatch(/Intent Guard/);
  });

  test("the pane lists the held command while the question is up", async ($, on) => {
    const seen: boolean[] = [];
    harness(on, async () => {
      const ui = await $.ui.mount({ plugin: "intent-guard", surface: "terminal", component: "Pane", requestId: "intent-guard", props: { title: "Intent Guard", isFocused: false, bodyColumns: 100, placement: "dock" } } as any);
      seen.push(!!(await ui.find({ type: "Text", text: /git reset --hard HEAD/ })), !!(await ui.find({ type: "Text", text: /discards git work/ })));
      await ui.unmount();
      return "Cancel";
    });
    await start($);
    await say($, "look at the logs");
    await sh($, "git reset --hard HEAD");
    expect(seen).toEqual([true, true]);
  });
});
