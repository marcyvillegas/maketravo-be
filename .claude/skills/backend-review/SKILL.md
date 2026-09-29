---
name: backend-review
description: Run the backend-reviewer agent on the current branch or explicitly named files/PR to find verified correctness and convention issues before a PR.
---

# backend-review

Use this command to run the repository's `backend-reviewer` agent for an
independent review. It is intended for a deeper pass before opening a PR, not
for repeated checks during implementation.

## Steps

1. If the user supplied a PR number or file list, pass that scope to the
   `backend-reviewer` agent. Otherwise, ask the agent to review the current
   branch against `main`.
2. Invoke the `backend-reviewer` agent using the Task/Agent tool with the
   review scope and the instructions in `.claude/agents/backend-reviewer.md`.
3. Wait for the agent to finish and present its verified findings. Do not
   duplicate or soften the agent's findings; if there are no findings, report
   that plainly.

The agent reads `CLAUDE.md`, reviews changed Python files under `src/` in full,
and reports only findings it verified against the current files. It does not
modify code.
