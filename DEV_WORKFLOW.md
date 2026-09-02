# Dev workflow with Claude Code skills & agents

This repo has no linter/formatter and no test suite yet (see `CLAUDE.md`), so
the conventions documented there — module layout, error-handling decorators,
Mongo model usage, the session/auth flow — are enforced by convention only.
The pieces below exist to make that enforcement cheap instead of relying on
memory during review.

| Name | Kind | Location | Purpose |
|---|---|---|---|
| `new-module` | skill | `.claude/skills/new-module/SKILL.md` | Scaffold a new `src/modules/<name>/` feature module |
| `convention-check` | skill | `.claude/skills/convention-check/SKILL.md` | Checklist pass over changed files before commit/PR |
| `backend-reviewer` | agent | `.claude/agents/backend-reviewer.md` | Deeper, independent review of a branch/diff before opening a PR |

## Day-to-day flow

1. **Start a new feature/resource** → `/new-module <name>`
   Generates `router.py`, `service.py`, `repositories.py`, `models.py`,
   `schemas.py`, `dependencies.py`, `exceptions.py` under
   `src/modules/<name>/`, wired into `create_app()` in `src/app.py`. It's a
   skeleton with `TODO`s, not a finished feature — fill in real fields and
   logic after it's generated.

2. **Implement the feature** as usual — edit the generated files, add
   endpoints, extend models.

3. **Before committing** → `/convention-check`
   Runs the checklist (naive timestamps, unwrapped Mongo calls, stray
   `HTTPException`, stdlib logging, credential logging, thin routers,
   dependency injection style, router registration) over your changed files
   and reports violations with file:line. Fast, inline, no subagent spin-up.

4. **Before opening a PR** (or when you want a second opinion) → ask for the
   `backend-reviewer` agent, or run it via Task/Agent with
   `subagent_type: backend-reviewer`. It re-reads `CLAUDE.md`, diffs your
   branch against `main`, reads full files (not just hunks) for context, and
   reports verified findings via `ReportFindings` — same conventions as
   `convention-check` but with full-file context and room to catch
   correctness bugs the checklist doesn't cover (bad awaits, N+1 queries,
   alias mismatches).

5. **Type check** → `pyright` (already configured via `pyproject.toml`) —
   run this regardless; none of the above substitute for it.

```
new-module  →  implement  →  convention-check  →  pyright  →  backend-reviewer  →  PR
 (scaffold)     (you)          (fast self-check)    (types)     (deeper review)
```

## When to use which

- Use **`convention-check`** for a quick pass on your own work-in-progress —
  it's cheap and inline, good to run repeatedly as you write code.
- Use **`backend-reviewer`** once, right before a PR — it's a full agent
  invocation (reads whole files, reasons harder) so it's worth more but
  costs more. Don't run it on every save.
- Use **`new-module`** only for genuinely new resources. For changes inside
  an existing module, just edit the files directly — don't re-scaffold.

## Keeping these in sync

If `CLAUDE.md`'s conventions change (e.g. the repo pattern changes, a new
mandatory decorator is introduced), update all three of these together —
`new-module`'s templates, `convention-check`'s checklist, and
`backend-reviewer`'s review criteria all encode the same rules and will
drift from `CLAUDE.md` (and from each other) if only one is updated.
