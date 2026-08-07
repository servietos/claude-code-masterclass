import { describe, expect, it } from 'vitest';
import { slugify } from '../src/slugify.js';

describe('slugify', () => {
  it('lowercases and joins with hyphens', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('strips non-alphanumerics', () => {
    expect(slugify('Hello, World! & Friends')).toBe('hello-world-friends');
  });

  it('trims leading and trailing hyphens', () => {
    expect(slugify('  --Claude Code--  ')).toBe('claude-code');
  });

  it('keeps digits', () => {
    expect(slugify('Module 05 CLI')).toBe('module-05-cli');
  });
});
