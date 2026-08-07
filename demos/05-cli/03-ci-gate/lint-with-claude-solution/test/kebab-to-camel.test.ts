import { describe, it, expect } from 'vitest';
import { kebabToCamel } from '../src/kebab-to-camel';

describe('kebabToCamel', () => {
  it('converts kebab-case to camelCase', () => {
    expect(kebabToCamel('background-color')).toBe('backgroundColor');
  });

  it('handles repeated hyphens', () => {
    expect(kebabToCamel('foo--bar')).toBe('fooBar');
  });

  it('uppercases digits-adjacent segments without leaving a hyphen', () => {
    expect(kebabToCamel('item-2-name')).toBe('item2Name');
  });

  it('returns an empty string for empty input', () => {
    expect(kebabToCamel('')).toBe('');
  });
});
