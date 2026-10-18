const PANE = "intent-guard";
const SHELL_TOOLS = new Set(["Bash", "PowerShell"]);
const PROMPT_WINDOW = 10;
const MESSAGE_WINDOW = 3;
const USER_ORIGINS = new Set(["composer", "bridge", "sdk"]);

const promptsRef = { plugin: "intent-guard", key: "prompts" };
const answerRef = { plugin: "intent-guard", key: "lastAnswer" };
const heldRef = { plugin: "intent-guard", key: "held" };

const SQL_TOOL = /(sqlcmd|Invoke-Sqlcmd|SqlConnection|SqlCommand|pyodbc|mssql-tools)/i;
const SQL_WRITE = /\b(DELETE|DROP|TRUNCATE|UPDATE|INSERT|MERGE|ALTER|CREATE|RESTORE|BACKUP)\b/i;
const INTERPRETERS = /^(python3?|py|node|bun|deno|bash|sh|zsh|pwsh|powershell|sqlcmd|psql|mysql|ssh|docker|kubectl|ruby|perl)$/i;
const DB_SCRIPT = /^\s*(do\s+|then\s+)?(&\s*)?((bash|sh|pwsh|powershell|python3?|py)\s+(-\S+\s+)*)?["']?\S*?[\w-]*(push|restore|apply|sync|migrat|seed|override)[\w-]*\.(sh|ps1|py|cmd)\b|^\s*sqlpackage\b/i;
const DB_WORD = /\b(db|sql|database|delta\w*)\b|-db\b|sqlpackage/i;

const FAMILIES = [
  {
    id: "file-delete",
    label: "deletes files",
    match: (c) => segments(c).some((s) => /^\s*(sudo\s+)?(xargs\s+(-\S+\s+)*)?(rm|rmdir|del|erase|ri)\s|['"]\s*(rm|rmdir)\s|Remove-Item|\s-delete\b|git\s+rm\b|shutil\.rmtree|os\.remove\(|\.unlink\(/i.test(s) && !/(\\|\/)(temp|tmp)[\\\/._-]|scratchpad/i.test(s) && !createdHere(s, c)),
    intent: /\b(delete|remove|rm|clean\s?up|wipe|purge|get rid|drop|do\s?n'?t need|no longer need|not needed|unused|l(ö|oe)sch\w*|entfern\w*)\b/i,
  },
  {
    id: "git-discard",
    label: "discards git work",
    match: (c) => /git\s+(-C\s+\S+\s+)?(checkout\s+(--|\.)|restore\b|stash\b(?!\s+(list|show))|reset\s+--hard|clean\s+-\w*f|branch\s+-D)|git\s+(-C\s+\S+\s+)?push\s+.*(--force|\s-f\b)/i.test(c),
    intent: /\b(revert|undo|discard|reset|restore|stash|throw away|roll\s?back|force|verwerf\w*|r(ü|ue)ckg(ä|ae)ngig|zur(ü|ue)cksetz\w*)\b/i,
  },
  {
    id: "git-commit",
    label: "commits",
    match: (c) => /git\s+(-C\s+\S+\s+)?commit\b/i.test(c),
    intent: /\b(commit\w*|check\s?in|einchecken)\b/i,
    messageScoped: true,
  },
  {
    id: "git-push",
    label: "pushes",
    match: (c) => /git\s+(-C\s+\S+\s+)?push\b/i.test(c),
    intent: /\bpush\w*\b/i,
    messageScoped: true,
  },
  {
    id: "pr-merge",
    label: "merges a pull request",
    match: (c) => /gh\s+pr\s+merge\b/i.test(c),
    intent: /\bmerge\w*\b/i,
    messageScoped: true,
  },
  {
    id: "package-publish",
    label: "publishes a package",
    match: (c) => /\b(npm|pnpm|yarn)\s+publish\b|dotnet\s+nuget\s+push\b|\btwine\s+upload\b/i.test(c),
    intent: /\b(publish\w*|release\w*|ship\w*)\b/i,
    messageScoped: true,
  },
  {
    id: "db-write",
    label: "writes to a database",
    match: (c, tool, scripts) => (SQL_TOOL.test(c) && (SQL_WRITE.test(c) || SQL_WRITE.test(scripts) || scripts === null)) || (segments(c).some((s) => DB_SCRIPT.test(s)) && DB_WORD.test(c)),
    intent: /\b(delete|update|insert|override|overwrite|restore|backup|drop|truncate|apply|migrate|seed|import|sync|copy|replace|write|change|modify|set|(ü|ue)berschreib\w*|wiederherstell\w*|einspiel\w*|l(ö|oe)sch\w*)\b/i,
  },
  {
    id: "remote-destroy",
    label: "deletes or stops remote resources",
    match: (c) => /\b(hcloud|az|gh|doctl)\s+(\S+\s+){0,3}(?<!-)\b(delete|remove|destroy|purge)\b|docker\s+(compose\s+down|rm\b|rmi\b|volume\s+rm|system\s+prune|image\s+prune|container\s+prune|network\s+rm|stop\b|kill\b)/i.test(c),
    intent: /\b(delete|remove|stop|tear\s?down|shut\s?down|decommission|destroy|clean\s?up|l(ö|oe)sch\w*|entfern\w*|stopp\w*|abschalt\w*)\b/i,
  },
  {
    id: "dns",
    label: "changes DNS",
    match: (c) => /(hcloud\s+zone|az\s+network\s+dns|import-zonefile|rrset)/i.test(c) && !/\s(list|describe|show)\b/i.test(c),
    intent: /\b(dns|zone|record\w*|delegation|nameserver\w*|cname|a-record)\b/i,
  },
  {
    id: "process-kill",
    label: "kills processes",
    match: (c) => !/chrome-devtools-mcp/i.test(c) && /Stop-Process|taskkill|(^|\s)kill\s|\bpkill\b|\bkillall\b/i.test(c),
    intent: /\b(kill|stop|restart|cycle|neu\s?start\w*|beend\w*)\b/i,
  },
  {
    id: "test-run",
    label: "runs tests",
    match: (c) => segments(c).some((s) => /^\s*(do\s+|then\s+)?((npx|pnpm|yarn|bunx|bun)\s+)?(vitest|ng\s+test|npm\s+(run\s+)?test|playwright\s+test|dotnet\s+test|pytest|python3?\s+-m\s+pytest)\b/i.test(s)),
    intent: /\b(test\w*|spec\w*|verify|verif\w*)\b/i,
    messageScoped: true,
  },
  {
    id: "mcp-delete",
    label: "deletes through an MCP tool",
    match: (c, tool) => /^mcp__.*(delete|remove|drop|purge|trash)/i.test(tool),
    intent: /\b(delete|remove|drop|purge|trash|l(ö|oe)sch\w*|entfern\w*)\b/i,
  },
];

const BLANKET = /\b(full permissions?|no checks?|volle (berechtigung|rechte))\b/i;
const AFFIRMATIVE = /^\s*(y|yes|yep|ja|go|go ahead|do it|do that|ok|okay|sure|mach|mach es|passt|proceed|continue|weiter)\b/i;
const GOAL = /(^|\s)\/goal\b/i;
const NEGATION = /\b(don'?t|do not|never|no|not|nicht|kein\w*|nie)\b(\s+\S+){0,2}\s*$/i;


export function register(on) {
  on("session.start", async ($, e, next) => {
    const result = await next(e);
    await $.state.set(heldRef, []);
    return result;
  });

  on("prompt.submit", async ($, e, next) => {
    const result = await next(e);
    if (!USER_ORIGINS.has(e.origin?.kind)) return result;
    const text = String(e.text ?? "").trim();
    if (text === "") return result;
    const { value: answer = "" } = await $.state.get(answerRef);
    const entry = AFFIRMATIVE.test(text) && answer ? `${text}\n${answer.slice(-2000)}` : text;
    const { value: prompts = [] } = await $.state.get(promptsRef);
    await $.state.set(promptsRef, [...prompts, entry].slice(-PROMPT_WINDOW));
    return result;
  });

  on("turn.complete", async ($, e, next) => {
    const result = await next(e);
    if (!e.agentId && typeof e.answer === "string") await $.state.set(answerRef, e.answer);
    return result;
  });

  on("tool.call", async ($, e, next) => {
    const isShell = SHELL_TOOLS.has(e.tool);
    if (!isShell && !String(e.tool).startsWith("mcp__")) return next(e);
    const command = isShell ? expandVars(stripData(String(e.command ?? ""))) : `${e.tool} ${JSON.stringify(stripReserved(e))}`;
    const scripts = isShell && SQL_TOOL.test(command) ? await readSqlScripts($, command) : "";
    const risky = FAMILIES.filter((f) => (f.id === "mcp-delete" ? !isShell : isShell) && f.match(command, e.tool, scripts));
    if (risky.length === 0) return next(e);

    const { value: prompts = [] } = await $.state.get(promptsRef);
    const unrequested = risky.filter((f) => !asked(f, prompts));
    if (unrequested.length === 0) return next(e);

    const cwd = await $.session.cwd().catch(() => "");

    const item = {
      id: e.tool_use_id ?? `${Date.now()}`,
      tool: e.tool,
      command: command.slice(0, 1500),
      cwd,
      agentId: e.agentId ?? null,
      reasons: unrequested.map((f) => f.label),
      lastPrompt: (prompts[prompts.length - 1] ?? "").split("\n")[0].slice(0, 300),
    };
    await pushHeld($, item).catch(() => {});
    try {
      await $.ui.open({ id: PANE, title: "Intent Guard" }).catch(() => {});
      const why = `you did not ask for it (${item.reasons.join(", ")})`;
      const who = item.agentId ? `Subagent ${item.agentId}` : "Claude";
      const where = isShell && cwd ? ` in ${cwd}` : "";
      const question = `${who} wants to run \`${brief(item.command, isShell, e.tool)}\`${where}, which ${item.reasons.join(" and ")}. Intent Guard held it because none of your recent prompts asked for that: run it?`;
      const choice = await $.ui.ask(question, { header: "Guard", options: ["Proceed", "Cancel"] });
      if (choice === "Proceed") return next(e);
      return { deny: `Intent Guard: the user pressed ${JSON.stringify(choice)} instead of Proceed for this command. It was held because ${why}. Do not retry it or reach the same result another way; ask the user.` };
    } catch {
      return { deny: `Intent Guard held this command because the user did not ask for it (${item.reasons.join(", ")}), and nobody could confirm it. Do not retry it or reach the same result another way; ask the user.` };
    } finally {
      await dropHeld($, item.id).catch(() => {});
    }
  });

  on("ui.render", { component: "Pane" }, async ($, e, next) => {
    if (e.requestId !== PANE) return next(e);
    const { value: held = [] } = await $.state.get(heldRef);
    const { Box, Text } = $.ui.resolve(e);
    if (held.length === 0) {
      return Box({ flexDirection: "column", paddingX: 1, children: [Text({ dimColor: true, children: "Nothing held." })] });
    }
    const rows = held.flatMap((h, i) => [
      Text({ bold: true, color: "yellow", children: `${i + 1}. ${h.tool}${h.agentId ? ` (agent ${h.agentId})` : ""}` }),
      Text({ children: h.command }),
      Text({ dimColor: true, children: `in ${h.cwd}` }),
      Text({ color: "yellow", children: `No request found for: ${h.reasons.join(", ")}` }),
      Text({ dimColor: true, children: `Your last prompt: ${h.lastPrompt || "(none)"}` }),
      Text({ children: " " }),
    ]);
    return Box({ flexDirection: "column", paddingX: 1, children: rows });
  });
}

function asked(family, prompts) {
  const recent = prompts.slice(-(family.messageScoped ? MESSAGE_WINDOW : PROMPT_WINDOW));
  const goals = family.messageScoped ? prompts.filter((p) => GOAL.test(p)) : [];
  return [...recent, ...goals].some((p) => (!family.messageScoped && BLANKET.test(p)) || mentions(family.intent, p));
}

function stripData(command) {
  const lines = command.split("\n");
  const kept = [];
  for (let i = 0; i < lines.length; i++) {
    kept.push(lines[i]);
    const m = lines[i].match(/<<-?\s*['"]?(\w+)['"]?/);
    if (!m) continue;
    const head = lines[i].slice(0, m.index).split(/&&|\|\||[;|(]/).pop().trim().split(/\s+/)[0] ?? "";
    if (INTERPRETERS.test(head.replace(/^.*[\\/]/, ""))) continue;
    while (i + 1 < lines.length && lines[i + 1].trim() !== m[1]) i++;
  }
  return kept.join("\n").replace(/(\s(-m|--message|--body|--title|--notes))\s+("(\\.|[^"\\])*"|'[^']*')/g, "$1 _");
}

function mentions(pattern, text) {
  const source = pattern.source.replace(/\\b$/, "(e|ed|es|ing|s|d)?\\b");
  const global = new RegExp(source, pattern.flags.includes("g") ? pattern.flags : `${pattern.flags}g`);
  for (const m of text.matchAll(global)) {
    if (!NEGATION.test(text.slice(Math.max(0, m.index - 40), m.index))) return true;
  }
  return false;
}

function createdHere(segment, command) {
  const targets = segment.replace(/^\s*(sudo\s+)?(rm|rmdir|del|erase)\s+/i, "").split(/\s+/).filter((t) => t && !t.startsWith("-"));
  if (targets.length === 0 || !/^\s*(sudo\s+)?(rm|rmdir|del|erase)\s/i.test(segment)) return false;
  const written = [...command.matchAll(/(>>?|\s-o|--output|Out-File|Set-Content)\s*["']?([^\s"'|;&]+)/gi)].map((m) => m[2]);
  return targets.every((t) => written.includes(t.replace(/^["']|["']$/g, "")));
}

async function readSqlScripts($, command) {
  const paths = [...segments(command).filter((s) => SQL_TOOL.test(s)).join(" ").matchAll(/\s-i\s+("([^"]+)"|'([^']+)'|(\S+))/g)].map((m) => m[2] ?? m[3] ?? m[4]);
  if (paths.length === 0) return "";
  try {
    const texts = await Promise.all(paths.map((p) => $.fs.read(p.replace(/^\/([a-z])\//i, "$1:/"))));
    return texts.join("\n");
  } catch {
    return null;
  }
}

function segments(command) {
  const out = [];
  let current = "";
  let quote = null;
  for (let i = 0; i < command.length; i++) {
    const ch = command[i];
    if (quote) {
      if (ch === quote && command[i - 1] !== "\\") quote = null;
      current += ch;
    } else if (ch === "'" || ch === '"') {
      quote = ch;
      current += ch;
    } else if (ch === ";" || ch === "\n" || ch === "|" || (ch === "&" && command[i + 1] === "&")) {
      out.push(current);
      current = "";
      if (command[i + 1] === ch) i++;
    } else {
      current += ch;
    }
  }
  out.push(current);
  return out;
}

function expandVars(command) {
  const vars = {};
  for (const m of command.matchAll(/(?:^|[\s;&])\$?([A-Za-z_]\w*)\s*=\s*("([^"]*)"|'([^']*)'|([^\s;&]+))/g)) vars[m[1]] = m[3] ?? m[4] ?? m[5];
  return command.replace(/\$\{?([A-Za-z_]\w*)\}?/g, (all, name) => vars[name] ?? all);
}


function brief(command, isShell, tool) {
  const text = isShell ? command.split("\n").find((l) => l.trim() !== "")?.trim() ?? "" : tool;
  return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

function stripReserved(e) {
  const { tool, tool_use_id, agentId, consent, ...rest } = e;
  return rest;
}

async function pushHeld($, item) {
  const { value: held = [] } = await $.state.get(heldRef);
  await $.state.set(heldRef, [...held, item]);
}

async function dropHeld($, id) {
  const { value: held = [] } = await $.state.get(heldRef);
  const rest = held.filter((h) => h.id !== id);
  await $.state.set(heldRef, rest);
  if (rest.length === 0) await $.ui.close({ id: PANE });
}
