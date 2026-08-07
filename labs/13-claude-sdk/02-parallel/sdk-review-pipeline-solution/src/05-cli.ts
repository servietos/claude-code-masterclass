import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";
import { reviewers } from "./reviewers.js";
import { runReviewer } from "./run-reviewer.js";
import { orchestrate, printSummary, VERDICT_EXIT_CODES } from "./orchestrate.js";

config({ path: fileURLToPath(new URL("../../../../../demos/13-claude-sdk/.env", import.meta.url)), quiet: true });

const filePath = process.argv[2];

if (!filePath) {
  console.error("usage: npm run review <file>");
  process.exit(1);
}

const fileContents = readFileSync(filePath, "utf8");
mkdirSync("results", { recursive: true });

const runs = await Promise.all(
  reviewers.map((config) => runReviewer(config, filePath, fileContents)),
);

for (const run of runs) {
  writeFileSync(`results/${run.reviewer}.json`, JSON.stringify(run.review, null, 2), "utf8");
}

const result = await orchestrate(runs.map((run) => run.review));
writeFileSync("results/orchestrated.json", JSON.stringify(result, null, 2), "utf8");
printSummary(result);

process.exit(VERDICT_EXIT_CODES[result.verdict]);
