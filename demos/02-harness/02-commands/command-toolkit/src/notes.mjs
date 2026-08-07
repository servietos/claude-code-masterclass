import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

export const GROUPS = {
  feat: 'Features',
  fix: 'Bug Fixes',
  perf: 'Performance',
  docs: 'Documentation',
  chore: 'Chores'
};

export const FALLBACK_GROUP = 'Other Changes';

export function groupFor(type) {
  return GROUPS[type] ?? FALLBACK_GROUP;
}

export function groupCommits(commits) {
  const grouped = new Map();
  for (const commit of commits) {
    const group = groupFor(commit.type);
    if (!grouped.has(group)) grouped.set(group, []);
    grouped.get(group).push(commit);
  }
  return grouped;
}

export function renderChangelog(commits, version) {
  const grouped = groupCommits(commits);
  const order = [...Object.values(GROUPS), FALLBACK_GROUP];
  const lines = [`# Release ${version}`, ''];
  for (const group of order) {
    const entries = grouped.get(group);
    if (!entries) continue;
    lines.push(`## ${group}`, '');
    for (const entry of entries) {
      lines.push(`- **${entry.scope}**: ${entry.subject} (@${entry.author})`);
    }
    lines.push('');
  }
  lines.push(`_${commits.length} commits in this release._`);
  return lines.join('\n');
}

export async function loadCommits() {
  const here = dirname(fileURLToPath(import.meta.url));
  const raw = await readFile(join(here, '..', 'data', 'commits.json'), 'utf8');
  return JSON.parse(raw);
}

const invokedDirectly = process.argv[1] === fileURLToPath(import.meta.url);

if (invokedDirectly) {
  const version = process.argv[2] ?? 'unreleased';
  const commits = await loadCommits();
  process.stdout.write(renderChangelog(commits, version) + '\n');
}
