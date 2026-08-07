import { describe, expect, it } from 'vitest';
import { kebabToCamel } from '../src/kebab-to-camel.js';

describe('kebabToCamel', () => {
  it('converts two segments', () => {
    expect(kebabToCamel('foo-bar')).toBe('fooBar');
  });

  it('converts three segments', () => {
    expect(kebabToCamel('a-b-c')).toBe('aBC');
  });

  it('converts four segments', () => {
    expect(kebabToCamel('one-two-three-four')).toBe('oneTwoThreeFour');
  });

  it('passes through a single segment', () => {
    expect(kebabToCamel('solo')).toBe('solo');
  });
});
