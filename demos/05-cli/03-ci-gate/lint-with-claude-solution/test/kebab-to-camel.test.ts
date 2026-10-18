import { describe, it, expect } from 'vitest';
import { kebabToCamel } from '../src/kebab-to-camel';

describe('kebabToCamel', () => {
  it('converts kebab-case to camelCase', () => {
    expect(kebabToCamel('background-color')).toBe('backgroundColor');
  });
});
