# Angular layout rules: buttons and action rows

## Layout Rules


| Rule | Detail |
| ---- | ------ |
| Button alignment | All button groups (`.actions`, `.section-actions`, `.hero-actions`) must use `justify-content: flex-end` so buttons sit at the right edge |
| Default button style | Orange fill (`var(--accent)`) with black text (`#0a0c10`), `font-weight: 700`. This is the global default — no extra class needed |
| Destructive buttons | Stop, Delete, Remove, Drop — use `.btn-danger`: solid red fill (`var(--danger)`) with black text (`#0a0c10`) |
| Exceptions | Icon/utility buttons (`.btn-close`, `.tree-btn`, `.template-card`) keep their own component-scoped overrides |

Back to the index: [angular-conventions](../SKILL.md)
