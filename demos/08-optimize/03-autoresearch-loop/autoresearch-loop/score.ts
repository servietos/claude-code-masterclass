import { readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const label = process.argv[2];
if (!label) {
  console.error("usage: npm run score -- <label>   (e.g. baseline, after)");
  process.exit(1);
}

const dir = join("runs", label);
if (!existsSync(dir)) {
  console.error(`no such run folder: ${dir}`);
  process.exit(1);
}

const REQUIRED_SECTIONS = [
  { key: "statusTable", test: (t: string) => /^\s*\|.*\bmodule\b/im.test(t) },
  { key: "completion", test: (t: string) => /\b\d{1,3}\s?%/.test(t) },
  { key: "gaps", test: (t: string) => /\b(planned|doing)\b/i.test(t) },
];

// Only a run that actually executed evaluate.py can quote its stdout line.
const EVALUATOR_EVIDENCE = /Evaluated\s+\d+\s+modules/i;

const normalize = (t: string) => t.replace(/\s+/g, " ").trim();

const files = readdirSync(dir).filter((f) => f.endsWith(".md")).sort();
const runs = files.map((f) => {
  const text = readFileSync(join(dir, f), "utf8");
  const aborted = normalize(text).length === 0 || /^ABORTED$/m.test(text);
  return {
    file: f,
    aborted,
    sectionsPresent: aborted ? 0 : REQUIRED_SECTIONS.filter((s) => s.test(text)).length,
    evaluatorEvidence: !aborted && EVALUATOR_EVIDENCE.test(text),
    normalized: normalize(text),
  };
});

// Aborted runs are excluded here, or two empty transcripts score as a matching pair.
const comparable = runs.filter((r) => !r.aborted);
let identicalOutputs = 0;
for (let i = 0; i < comparable.length; i++) {
  for (let j = i + 1; j < comparable.length; j++) {
    if (comparable[i].normalized === comparable[j].normalized) identicalOutputs++;
  }
}

const mean = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);

const result = {
  label,
  runs: runs.length,
  identicalOutputs,
  sectionsPresent: Number(mean(comparable.map((r) => r.sectionsPresent)).toFixed(2)),
  evaluatorEvidence: Number(mean(comparable.map((r) => (r.evaluatorEvidence ? 1 : 0))).toFixed(2)),
  abortRate: Number(mean(runs.map((r) => (r.aborted ? 1 : 0))).toFixed(2)),
  perRun: runs.map(({ file, aborted, sectionsPresent, evaluatorEvidence }) => ({
    file,
    aborted,
    sectionsPresent,
    evaluatorEvidence,
  })),
};

writeFileSync(`${label}.json`, JSON.stringify(result, null, 2) + "\n");

console.log(`${label}: ${result.runs} runs`);
console.log(`  identical_outputs  ${result.identicalOutputs} of ${(comparable.length * (comparable.length - 1)) / 2} pairs`);
console.log(`  sections_present   ${result.sectionsPresent} of ${REQUIRED_SECTIONS.length}`);
console.log(`  evaluator_evidence ${result.evaluatorEvidence}`);
console.log(`  abort_rate         ${result.abortRate}`);

if (existsSync("baseline.json") && label !== "baseline") {
  const base = JSON.parse(readFileSync("baseline.json", "utf8"));
  const target = process.env.TARGET_METRIC ?? "sectionsPresent";
  const improved = result[target as keyof typeof result] > base[target];
  const others = ["identicalOutputs", "sectionsPresent", "evaluatorEvidence"].filter((k) => k !== target);
  // A regression of more than one unit on any untargeted metric blocks the promotion.
  const regressed = others.filter((k) => base[k] - (result as never)[k] > 1);
  const promote = improved && regressed.length === 0 && result.abortRate === 0;

  console.log(`\ntarget metric      ${target}: ${base[target]} -> ${result[target as keyof typeof result]}`);
  console.log(`regressed          ${regressed.length ? regressed.join(", ") : "none"}`);
  console.log(`DECISION           ${promote ? "PROMOTE" : "REVERT"}`);
}
