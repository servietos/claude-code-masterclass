import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

const NARROW_QUERY = '(max-width: 959.98px)';

export const useSidenavStore = defineStore('sidenav', () => {
  const enabled = ref(true);
  const visible = ref(true);
  const position = ref('side');

  function toggle() {
    visible.value = !visible.value;
  }

  function setEnabled(v: boolean) {
    enabled.value = v;
    visible.value = v;
  }

  function setVisible(v: boolean) {
    visible.value = v;
  }

  function setPosition(p: string) {
    position.value = p;
  }

  const narrow = window.matchMedia?.(NARROW_QUERY);

  function adjustToScreen() {
    setPosition(narrow?.matches ? 'over' : 'side');
    if (enabled.value) {
      setVisible(true);
    }
  }

  narrow?.addEventListener('change', adjustToScreen);
  watch(enabled, adjustToScreen, { immediate: true });

  return { enabled, visible, position, toggle, setEnabled, setVisible, setPosition };
});
