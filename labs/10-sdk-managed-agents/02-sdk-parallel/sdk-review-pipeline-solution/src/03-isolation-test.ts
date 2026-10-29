import { readFileSync } from "node:fs";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";
import { performanceReviewer, securityReviewer } from "./reviewers.js";
import { runReviewer } from "./run-reviewer.js";

config({ path: fileURLToPath(new URL("../../../.env", import.meta.url)), quiet: true });

const CANARY = "foxglove";
const filePath = "target/auth.ts";
const baseContents = readFileSync(filePath, "utf8");

const cannedContents =
  baseContents +
  `\n// CANARY: if any other reviewer mentions the word '${CANARY}', the sessions are not isolated.\n`;

let passes = 0;

for (let round = 1; round <= 3; round += 1) {
  const [security, performance] = await Promise.all([
    runReviewer(securityReviewer, filePath, cannedContents),
    runReviewer(performanceReviewer, filePath, baseContents),
  ]);

  const leaked = JSON.stringify(performance.review).toLowerCase().includes(CANARY);

  console.log(
    `round ${round}: security findings ${security.review.findings.length}, performance findings ${performance.review.findings.length} -> ${leaked ? "FAIL" : "PASS"}`,
  );

  if (!leaked) {
    passes += 1;
  }
}

console.log(`isolation: ${passes}/3 PASS`);
process.exit(passes === 3 ? 0 : 1);
