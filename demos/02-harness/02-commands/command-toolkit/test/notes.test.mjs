import test from 'node:test';
import assert from 'node:assert/strict';
import { GROUPS, FALLBACK_GROUP, groupFor, groupCommits, renderChangelog, loadCommits } from '../src/notes.mjs';

test('known types map to their group heading', () => {
  assert.equal(groupFor('feat'), 'Features');
  assert.equal(groupFor('fix'), 'Bug Fixes');
});

test('unknown types fall back to Other Changes', () => {
  assert.equal(groupFor('refactor'), FALLBACK_GROUP);
});

test('groupCommits buckets every commit', async () => {
  const commits = await loadCommits();
  const grouped = groupCommits(commits);
  const total = [...grouped.values()].reduce((sum, list) => sum + list.length, 0);
  assert.equal(total, commits.length);
});

test('renderChangelog emits the version heading and a commit count', async () => {
  const commits = await loadCommits();
  const output = renderChangelog(commits, '2.4.0');
  assert.match(output, /^# Release 2\.4\.0$/m);
  assert.match(output, /## Features/);
  assert.match(output, new RegExp(`_${commits.length} commits in this release\\._`));
});

test('every configured group has a non-empty heading', () => {
  for (const heading of Object.values(GROUPS)) {
    assert.ok(heading.length > 0);
  }
});
