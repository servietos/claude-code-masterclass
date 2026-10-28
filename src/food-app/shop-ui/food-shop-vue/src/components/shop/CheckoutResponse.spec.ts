import { mount, type VueWrapper } from '@vue/test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import CheckoutResponse from './CheckoutResponse.vue';

vi.mock('@/services/logger', () => ({
  logger: { logEvent: vi.fn() },
}));

describe('CheckoutResponse', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    wrapper = mount(CheckoutResponse);
  });

  it('should create', () => {
    expect(wrapper.vm).toBeTruthy();
  });
});
