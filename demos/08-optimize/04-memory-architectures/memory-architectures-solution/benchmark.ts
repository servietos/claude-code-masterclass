import { readFile } from "fs/promises";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { getEncoding } from "js-tiktoken";

const __dirname = dirname(fileURLToPath(import.meta.url));

function countTokens(text: string): number {
  const enc = getEncoding("cl100k_base");
  return enc.encode(text).length;
}

async function readRelative(relPath: string): Promise<string> {
  return readFile(join(__dirname, relPath), "utf-8");
}

function pad(str: string, width: number): string {
  return str.padEnd(width);
}

function padLeft(str: string, width: number): string {
  return str.padStart(width);
}

async function main() {
  const incidents = await readRelative("corpus/incidents.md");
  const decisions = await readRelative("corpus/decisions.md");
  const teamNotes = await readRelative("corpus/team-notes.md");

  const corpusTokens =
    countTokens(incidents) + countTokens(decisions) + countTokens(teamNotes);

  const fullCorpus = `${incidents}\n\n${decisions}\n\n${teamNotes}`;
  const question =
    "Question: What was the root cause of INC-001, and which ADR was adopted as a direct consequence of that incident?";
  const inContextPrompt = `Below is the complete knowledge base for this project.\n\n---\n\n${fullCorpus}\n\n---\n\n${question}`;
  const inContextTokens = countTokens(inContextPrompt);

  const stateFile = await readRelative("approaches/statefile/STATE.md");
  const statefilePrompt = `${stateFile}\n\n${question}`;
  const statefileTokens = countTokens(statefilePrompt);

  const memoryIndex = await readRelative("approaches/auto-memory/MEMORY.md");
  const recalledMemory = await readRelative(
    "approaches/auto-memory/project-inc-001-pool-exhaustion.md"
  );
  const autoMemoryPrompt = `${memoryIndex}\n\n${recalledMemory}\n\n${question}`;
  const autoMemoryTokens = countTokens(autoMemoryPrompt);

  const graphPrompt = await readRelative(
    "approaches/knowledge-graph/prompt.md"
  );
  const graphTokens = countTokens(graphPrompt);

  const TURNS = 30;
  const INDEX_LINE_LIMIT = 200;
  const INDEX_BYTE_LIMIT = 25 * 1024;

  const indexLines = memoryIndex.trimEnd().split("\n").length;
  const indexBytes = Buffer.byteLength(memoryIndex, "utf-8");

  const rows: Array<{
    name: string;
    tokensPerQuestion: number;
    tokensPerSession: number;
    recall: string;
  }> = [
    {
      name: "In-context",
      tokensPerQuestion: inContextTokens,
      tokensPerSession: inContextTokens * TURNS,
      recall: "Highest",
    },
    {
      name: "Statefile",
      tokensPerQuestion: statefileTokens,
      tokensPerSession: statefileTokens * TURNS,
      recall: "Good",
    },
    {
      name: "Auto-memory",
      tokensPerQuestion: autoMemoryTokens,
      tokensPerSession: autoMemoryTokens * TURNS,
      recall: "Good (index-capped)",
    },
    {
      name: "Knowledge graph",
      tokensPerQuestion: graphTokens,
      tokensPerSession: graphTokens * TURNS,
      recall: "Strong (relational)",
    },
  ];

  const col1 = 16;
  const col2 = 17;
  const col3 = 22;
  const col4 = 21;

  const header =
    `| ${pad("Approach", col1)} | ${pad("Tokens/question", col2)} | ${pad("Tokens/session (×30)", col3)} | ${pad("Recall strength", col4)} |`;
  const divider =
    `|${"-".repeat(col1 + 2)}|${"-".repeat(col2 + 2)}|${"-".repeat(col3 + 2)}|${"-".repeat(col4 + 2)}|`;

  console.log("Memory Architecture Benchmark");
  console.log("==============================");
  console.log("");
  console.log(`Corpus size: ${corpusTokens} tokens (incidents + decisions + team-notes)`);
  console.log("");
  console.log(header);
  console.log(divider);

  for (const row of rows) {
    console.log(
      `| ${pad(row.name, col1)} | ${padLeft(String(row.tokensPerQuestion), col2)} | ${padLeft(String(row.tokensPerSession), col3)} | ${pad(row.recall, col4)} |`
    );
  }

  console.log("");
  console.log("Auto-memory index budget (MEMORY.md loads at session start):");
  console.log(`  Lines: ${indexLines} of ${INDEX_LINE_LIMIT}`);
  console.log(`  Bytes: ${indexBytes} of ${INDEX_BYTE_LIMIT}`);
  console.log(
    `  Recurring: ${countTokens(memoryIndex)} tokens/turn for the index, ${countTokens(recalledMemory)} once for the file it pointed at`
  );
  console.log("");
  console.log("Decision guide:");
  console.log("  One-shot task, corpus loaded once       => use in-context");
  console.log("  Ongoing project, stable facts           => use statefile");
  console.log("  Corrections that outlive the session    => use auto-memory");
  console.log("  Entity-relation queries, many turns     => use knowledge graph");
  console.log("");
  console.log("Run: npm run benchmark");
}

main();
