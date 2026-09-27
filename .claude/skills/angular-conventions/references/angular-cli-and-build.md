# Angular CLI, dev commands and deployment

## Code Generation


Use Angular CLI rather than hand-writing the initial file structure.

```bash
ng generate component my-component
ng generate service my-service
ng generate directive my-directive
ng generate pipe my-pipe
```

## Development Commands


| Command            | Use                                        |
| ------------------ | ------------------------------------------ |
| `ng serve`         | Start the local Angular development server |
| `ng build`         | Create a production build                  |
| `ng build --watch` | Rebuild continuously during development    |

## Deployment Note


Angular projects in this repository are typically deployed to Azure Static Web Apps or Azure Container Apps. Use the project-specific deployment scripts and documentation instead of inventing a new deployment path.

Back to the index: [angular-conventions](../SKILL.md)
