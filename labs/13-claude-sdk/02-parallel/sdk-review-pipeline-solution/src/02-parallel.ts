import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";
import { reviewers } from "./reviewers.js";
import { runReviewer } from "./run-reviewer.js";

config({ path: fileURLToPath(new URL("../../../../../demos/13-claude-sdk/.env", import.meta.url)), quiet: true });

const filePath = "target/auth.ts";
const fileContents = readFileSync(filePath, "utf8");

mkdirSync("results", { recursive: true });

const startedAt = Date.now();

const runs = await Promise.all(
  reviewers.map((config) => runReviewer(config, filePath, fileContents)),
);

for (const run of runs) {
  writeFileSync(
    `results/${run.reviewer}.json`,
    JSON.stringify(run.review, null, 2),
    "utf8",
  );
  console.log(
    `${run.reviewer}: ${run.review.findings.length} findings, verdict ${run.review.overall_verdict}, cost $${run.costUsd.toFixed(4)}, ${run.durationMs}ms`,
  );
}

const wallClockMs = Date.now() - startedAt;
const serialMs = runs.reduce((sum, run) => sum + run.durationMs, 0);

console.log(`wall clock: ${wallClockMs}ms`);
console.log(`sum of reviewer durations: ${serialMs}ms`);
console.log(`total cost: $${runs.reduce((s, r) => s + r.costUsd, 0).toFixed(4)}`);
