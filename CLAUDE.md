# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

MakeTravo backend: a FastAPI service backed by MongoDB (via async PyMongo) and Firebase Admin (Auth). Python 3.12.

## Commands

There is no Makefile/task runner — everything goes through the venv directly.

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run the dev server (reload on change)
uvicorn main:app --reload

# Type check (pyright is installed; config lives in pyproject.toml)
pyright

# Run tests (requires local MongoDB on localhost:27017 — see src/tests/)
pytest
```

Dependencies (runtime + dev) are declared in `pyproject.toml` under `[project.dependencies]` / `[project.optional-dependencies].dev` — there is no `requirement.txt` anymore. `src/tests/` has integration tests under `src/tests/integration/`; they spin up the app in-process (`httpx` + `asgi-lifespan`) against a local MongoDB and reset it via `pytest_sessionstart`/`pytest_sessionfinish` in `conftest.py`.

No linter/formatter (ruff/black/flake8) is configured in this repo currently.

## Configuration

Settings are loaded via `pydantic-settings` in [src/config.py](src/config.py) from a `.env` file (see [.env.sample](.env.sample) for required keys). All required env vars (Firebase creds, Mongo URI, etc.) must be set or `Settings()` will fail at import time — `main.py` imports `create_app()` which reads settings eagerly.

`.env` and `firebase.txt` are gitignored — never commit real credentials into tracked files.

## Architecture

### App composition

[src/app.py](src/app.py)'s `create_app()` is the single place wiring things together: CORS, global exception handlers, and one `MongoConnection` opened at startup and closed at shutdown via the `lifespan` context manager. The live Mongo connection and settings are stashed on `app.state` (not module globals) so request-scoped dependencies can reach them — see `get_database` in [src/mongodb/dependencies.py](src/mongodb/dependencies.py).

`main.py` just does `app = create_app()` — that's the ASGI entrypoint uvicorn points at.

### Module layout (`src/modules/<name>/`)

Each feature module follows the same file split:
- `router.py` — FastAPI routes; thin, delegates to `service.py`
- `service.py` — business logic, orchestrates repos/clients; takes dependencies as explicit keyword args rather than importing them directly (keeps it testable without FastAPI)
- `repositories.py` — data access, one function per Mongo operation, returns typed models
- `models.py` — Pydantic models (Mongo documents)
- `schemas.py` — request/response bodies (API-facing shapes, may differ from stored models)
- `dependencies.py` — FastAPI `Depends`-based providers, exposed as `XxxDep = Annotated[...]` type aliases
- `exceptions.py` — module-specific `BaseDomainException` subclasses

Repositories use the "constructor function returning a `NamedTuple` of closures" pattern rather than classes — e.g. `mongo_user_repo(db)` in [src/modules/users/repositories.py](src/modules/users/repositories.py) returns a `UserRepo` NamedTuple of async functions closed over `db`. The `Protocol`/`NamedTuple` combo defines the repo's interface independent of the Mongo implementation.

New routers must be registered manually in `create_app()` in [src/app.py](src/app.py) — nothing is auto-discovered.

### Sessions/auth flow

Auth is cookie-session based on top of Firebase ID tokens, not raw bearer-token-per-request:
1. Client obtains a Firebase ID token, POSTs it as a Bearer credential to `POST /api/sessions`.
2. [src/modules/sessions/service.py](src/modules/sessions/service.py) verifies the token via `FirebaseAuthClient.create_session` ([src/firebase/auth_client.py](src/firebase/auth_client.py)), which also enforces a max auth age (`max_auth_age_seconds`) — a valid-but-stale sign-in is rejected (`StaleSignIn`).
3. On success, a Firebase session cookie is minted and set via `create_cookie()` ([src/shared/cookie.py](src/shared/cookie.py)); cookie name is hardcoded to `__session` (required by Firebase Hosting).
4. Identity for the local `User` upsert always comes from the **verified token claims**, never from the request body — the body's `user_data` is only a fallback for display fields (name/photo) the token doesn't carry. Never log the raw token or cookie value.

`FirebaseAuthClient` is built once per process via `@lru_cache` in [src/firebase/dependencies.py](src/firebase/dependencies.py) (building it initializes the Firebase Admin app). Override `get_firebase_auth` via `app.dependency_overrides` in tests rather than constructing the client directly.

### Mongo models

All Mongo-backed Pydantic models extend `MongoModel` ([src/mongodb/models.py](src/mongodb/models.py)), which centralizes the `_id`/`id` aliasing:
- `Model.from_mongo(doc)` — converts a raw document (and its `ObjectId`) into the model
- `instance.to_mongo()` — dumps back to a dict for insert/update, dropping `id` (Mongo assigns `_id`)

Always use `utcnow()` from that module instead of `datetime.utcnow()` (the latter returns a naive datetime).

### Error handling

Every domain-level error is a `BaseDomainException` subclass ([src/shared/exceptions/base.py](src/shared/exceptions/base.py)) carrying `message`, `internal_code`, `status_code`, and an optional `scope`. Two global handlers are registered in [src/shared/exceptions/global_exception.py](src/shared/exceptions/global_exception.py):
- `BaseDomainException` → serialized as `{"success": false, "error": {code, message, trace_id}}` with its own status code, logged at `error`.
- Anything else (unhandled) → safety net returning a generic 500 with the same envelope shape, logged at `critical` with a trace ID. Never let internal exception details leak to the response.

Infra-specific errors are translated to domain exceptions at the boundary via decorators, not scattered try/except in business logic:
- `@handle_mongo_error` ([src/mongodb/exceptions.py](src/mongodb/exceptions.py)) maps PyMongo exceptions (`DuplicateKeyError`, timeouts, connection failures, etc.) to typed `DatabaseError` subclasses — walks `type(e).__mro__` against an error map so subclasses of mapped exceptions resolve correctly. Apply this to every repository function that touches Mongo.
- `@handle_firebase_auth_error` ([src/firebase/exceptions.py](src/firebase/exceptions.py)) does the same for `firebase_admin` auth errors (expired/revoked tokens, disabled users, etc.).

When adding a new failure mode, add a `BaseDomainException` subclass in the owning module's `exceptions.py` (or `src/shared/exceptions/` if cross-cutting) rather than raising bare exceptions or HTTPException.

### Logging

Use `scope_logger()` from [src/logging.py](src/logging.py), not the stdlib `logging` module directly. Called with no args, it infers the scope from the caller's module name via `inspect`; pass an explicit string to override. All logs go through a single `maketravo` logger with a formatter that includes the scope.
