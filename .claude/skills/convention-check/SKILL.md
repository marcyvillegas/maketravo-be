---
name: convention-check
description: Check staged/changed backend code against this repo's architecture conventions from CLAUDE.md before commit or PR (error handling, logging, module layout, Mongo model usage, auth rules). No formatter/linter is configured, so this is the closest thing to one.
---

# convention-check

This repo has no ruff/black/flake8 configured, and pyright only catches
types — not the architectural conventions in `CLAUDE.md`. This skill is a
manual checklist to run over changed files before a commit or PR, so drift
from those conventions gets caught early.

## Scope

By default, check files changed vs `main`:

```bash
git diff --name-only main...HEAD -- '*.py'
git status --porcelain -- '*.py'
```

If `args` names specific files/modules, check only those instead.

## Checklist

Work through each item against the changed files. For every violation found,
report the file:line and a one-line fix suggestion. Skip items that don't
apply (e.g. no repo changes → skip the repo checks).

1. **Naive timestamps** — `grep -rn "datetime.utcnow()" <files>`. Must use
   `utcnow()` from `src.mongodb.models` instead.

2. **Bare HTTPException in business logic** — `grep -rn "HTTPException" <changed service.py/repositories.py files>`.
   Domain errors belong in `exceptions.py` as `BaseDomainException`
   subclasses, raised from `service.py`/`repositories.py`. `HTTPException`
   should not appear outside `router.py` (and ideally not even there).

3. **Unwrapped Mongo calls** — for any new/changed function in a
   `repositories.py` that calls `col.<mongo_method>`, confirm it's decorated
   with `@handle_mongo_error` from `src.mongodb.exceptions`.

4. **Stdlib logging** — `grep -rn "^import logging\|logging.getLogger\|print(" <changed files>`.
   Should use `scope_logger()` from `src.logging` instead.

5. **Credential/token logging** — `grep -rniE "logger\.(info|debug|warning|error).*\b(token|cookie|credential)\b" <changed files>`.
   Read each hit; the raw token/cookie value must never be interpolated into
   a log message (see the comment in `src/modules/sessions/service.py`).

6. **Models not extending MongoModel** — any new Pydantic model in a
   `models.py` under `src/modules/` that represents a stored document should
   subclass `MongoModel` (`src.mongodb.models`), not bare `BaseModel`.

7. **Identity from request body** — in any session/auth-related code, confirm
   user identity (uid/email) is taken from verified token claims, never from
   client-supplied request body fields. Body data may only fill display
   fields as a fallback.

8. **Router thinness** — skim each changed `router.py`. It should only parse
   input via `Depends`/path/query params, call into `service.py`, and shape
   the response — no direct repo/DB calls, no branching business logic.

9. **Service dependency injection** — skim each changed `service.py`. Repos
   and other collaborators should arrive as explicit keyword arguments, not
   be imported and instantiated inside the function.

10. **New router registration** — if a new `router.py` was added under
    `src/modules/<name>/`, confirm `src/app.py` imports it and calls
    `app.include_router(...)` for it.

11. **Env/secrets** — `grep -rn "firebase.txt\|\.env" <changed files>` and
    confirm no real credential values were added to a tracked file.

## Output

Report as a short list grouped by checklist item number, each with
file:line and fix. If everything passes, say so plainly — don't pad the
report with restated rules that had no violations.

This skill does not edit files on its own. Only make fixes if the user asks
you to apply them after seeing the report.
