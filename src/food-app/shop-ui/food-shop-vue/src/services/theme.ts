import { readonly, ref, type Ref } from 'vue';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'food-shop-theme';

let state: Ref<Theme> | null = null;

function initialTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function apply(theme: Theme) {
  document.documentElement.setAttribute('data-theme', theme);
}

export function useTheme() {
  if (!state) {
    state = ref<Theme>(initialTheme());
    apply(state.value);
  }
  const current = state;

  function toggle() {
    const next: Theme = current.value === 'dark' ? 'light' : 'dark';
    current.value = next;
    localStorage.setItem(STORAGE_KEY, next);
    apply(next);
  }

  return { theme: readonly(current), toggle };
}
