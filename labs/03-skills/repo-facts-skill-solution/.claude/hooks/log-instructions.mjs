import { appendFileSync } from 'node:fs';
import { join } from 'node:path';

const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
const input = JSON.parse(Buffer.concat(chunks).toString('utf8'));

const entry = {
  at: new Date().toISOString(),
  load_reason: input.load_reason,
  file_path: input.file_path,
  globs: input.globs ?? null,
  trigger_file_path: input.trigger_file_path ?? null,
};

appendFileSync(join(input.cwd, 'instructions-log.txt'), JSON.stringify(entry) + '\n');
