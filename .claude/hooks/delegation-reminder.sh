#!/bin/bash
# UserPromptSubmit hook: re-inject the delegation/skill routing rule every turn.
# Counters context-decay of the CLAUDE.md "delegate to experts" guidance.
# stdout (exit 0) is added to the model context. Must never block the prompt.

cat <<'EOF'
[Routing check — before doing domain work on the main thread]
Delegate to the owning expert (default working mode, not a fallback):
- Angular components / services / state   -> angular-expert
- .NET REST API / EF Core / migrations     -> dotnet-expert
- SSH deploy to an Ubuntu host / GitHub Actions -> github-devops-agent
- QA / screenshots / Lighthouse            -> playwright-expert (reports only; only when explicitly requested)
Check .claude/skills for a matching skill/convention BEFORE implementing.
Parallelize independent work across agents whenever subtasks are independent.
Skip routing only for trivial one-liners or pure conversation.
EOF

exit 0
