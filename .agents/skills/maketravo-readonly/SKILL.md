---
name: maketravo-readonly
description: Answer questions about the MakeTravo backend by inspecting the repository without changing files. Use for codebase orientation, tracing request flows, and explaining project conventions.
---

# MakeTravo read-only guide

Use this skill only for questions about the MakeTravo backend repository. Inspect the current source and project guidance, then explain findings with file paths and relevant symbols.

For feature modules, trace the request through the router, service, dependencies, and repository as applicable. Use `CLAUDE.md` and nearby implementations as the source for project conventions; distinguish documented rules from observations in code.

This is an inspection-only workflow. Do not edit files, generate scaffolding, stage or commit changes, push, or run commands that modify project state. Do not run tests or builds. If the user wants changes, explain the findings and wait for a separate implementation request.

Keep answers concise and specific. If the inspected code does not establish an answer, say what is uncertain rather than guessing.
