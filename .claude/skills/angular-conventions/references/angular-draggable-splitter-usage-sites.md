# Splitter usage sites

## Where it's used

| Page | Component | storageKey | initial / min / max (px) | Panes |
| --- | --- | --- | --- | --- |
| `/` (home) | `home/home-chat/home-chat.component` | `home-chat-split` | 256 / 200 / 420 | chat ↔ chat-history `<aside>` (`bg-surface-alt`) |
| `/tasks/new`, `/tasks/:id` | `tasks/edit-task/edit-task.component` | `edit-task-split` | 416 / 320 / 640 | chat ↔ right meta panel |

Both previously used static `grid-template-columns` (`[1fr_16rem]`, `[1fr_26rem]`);
`ux-splitter` replaced only that inner two-column body grid — outer frames,
`bg-ink` header bars, and `h-[calc(100vh-160px)]` height math stay intact.


Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)
