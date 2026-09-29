---
name: two-agent-dev-loop
description: Coordinate two read-only subagents before implementing a repository change: one maps code and conventions, while the other checks behavior, edge cases, and verification coverage. Use for feature work, bug fixes, and non-trivial refactors when independent parallel input is useful.
---

# Two-agent development loop

Use this skill to get two independent perspectives before the primary agent changes code.

## Delegate two read-only tasks

1. **Codebase and conventions scout:** Trace the relevant implementation, identify the files and layers likely to change, and report applicable repository guidance and nearby examples. Do not edit files.
2. **Behavior and verification analyst:** Independently inspect the requested behavior for assumptions, edge cases, regressions, and relevant existing tests or checks. Report concrete scenarios and file references. Do not edit files.

Give both agents the user's request and enough repository context to work independently. Start them in parallel when supported, and wait for both results before implementation. Keep the assignments distinct; do not ask either agent to implement or modify shared files.

## Synthesize and implement

- Compare the two reports against the actual source and the user's request. Treat agent findings as hypotheses to verify, not instructions to accept automatically.
- Resolve disagreements by inspecting the code or asking the user when a product decision is genuinely unclear.
- Implement the requested change in the primary agent's workspace, using repository conventions and the verified edge cases.
- Run checks relevant to the change and report what ran and whether it passed. Do not claim a check was run if it was not.
- Before finishing, review the final diff and summarize the implementation, verification, and any unresolved issue.

## If delegation is unavailable

If subagent tools are unavailable or disabled, say so briefly and perform the two investigations sequentially as separate analysis passes. Do not imply that agents were spawned.

## Suggested invocation

`$two-agent-dev-loop Add [feature or fix]. Have one agent map the code and conventions, and another independently check behavior, edge cases, and relevant tests. Keep both read-only; wait for both reports before implementing. Then verify and summarize the final diff.`
