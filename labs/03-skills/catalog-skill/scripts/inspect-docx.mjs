import { readFile } from "node:fs/promises";
import JSZip from "jszip";

const zip = await JSZip.loadAsync(await readFile(process.argv[2]));
const xml = await zip.file("word/document.xml").async("string");
const text = [...xml.matchAll(/<w:t[^>]*>([^<]*)<\/w:t>/g)].map((m) => m[1]);
const tables = (xml.match(/<w:tbl>/g) ?? []).length;
console.log(`parts: ${Object.keys(zip.files).length}`);
console.log(`tables: ${tables}`);
console.log(`text runs: ${text.length}`);
console.log(text.join(" | "));
