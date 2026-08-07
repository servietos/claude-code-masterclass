import { describe, it, expect } from 'vitest';
import { slugify } from '../src/slugify';

describe('slugify', () => {
  it('converts text to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('strips leading and trailing whitespace', () => {
    expect(slugify('  Hello World  ')).toBe('hello-world');
  });

  it('strips leading and trailing hyphens', () => {
    expect(slugify('--Hello World--')).toBe('hello-world');
  });

  it('returns an empty string for empty input', () => {
    expect(slugify('')).toBe('');
  });
});
