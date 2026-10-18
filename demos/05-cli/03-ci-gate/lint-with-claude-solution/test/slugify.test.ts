import { describe, it, expect } from 'vitest';
import { slugify } from '../src/slugify';

describe('slugify', () => {
  it('converts text to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });
});
