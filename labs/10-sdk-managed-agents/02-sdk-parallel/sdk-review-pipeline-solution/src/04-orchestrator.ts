import { readFileSync, writeFileSync } from "node:fs";
import { config } from "dotenv";
import { fileURLToPath } from "node:url";
import { type Review } from "./reviewers.js";
import { orchestrate, printSummary } from "./orchestrate.js";

config({ path: fileURLToPath(new URL("../../../../../demos/10-sdk-managed-agents/.env", import.meta.url)), quiet: true });

const reviews: Review[] =["security", "performance", "style"].map(
  (name) => JSON.parse(readFileSync(`results/${name}.json`, "utf8")) as Review,
);

const result = await orchestrate(reviews);

writeFileSync("results/orchestrated.json", JSON.stringify(result, null, 2), "utf8");
printSummary(result);
