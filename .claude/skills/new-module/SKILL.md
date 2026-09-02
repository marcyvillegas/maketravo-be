---
name: new-module
description: Scaffold a new src/modules/<name>/ feature module (router, service, repositories, models, schemas, dependencies, exceptions) following this repo's conventions from CLAUDE.md.
---

# new-module

Scaffolds a new feature module under `src/modules/<name>/` that matches the
patterns already used by `src/modules/users/` and `src/modules/sessions/`.
Use this whenever the user asks to add a new domain/resource (e.g. "add a
trips module", "new module for bookings").

## Input

`args` is the module name, e.g. `trips`. Derive:
- `module` = snake_case plural folder name (e.g. `trips`)
- `Model` = singular PascalCase model name (e.g. `Trip`)
- `collection` = Mongo collection name, usually same as `module`

If `args` is missing or ambiguous, ask the user for the module name and the
primary model name before generating anything.

## Steps

1. Confirm `src/modules/<module>/` does not already exist. If it does, stop
   and ask the user how to proceed instead of overwriting files.
2. Create these files (see templates below), adapting names/fields to what
   the user described. Never invent extra endpoints, fields, or files beyond
   the standard 7 — keep it a minimal skeleton the user fills in.
3. Read `src/app.py` and add the new router import + `app.include_router(...)`
   call in the same style as the existing (commented-out) `users_router`
   lines — do not leave it unregistered, and do not remove other routers.
4. Run `pyright` and fix any type errors the skeleton introduces before
   reporting done.
5. Tell the user the module was created and that they still need to fill in
   real fields/business logic — this skill only produces the skeleton.

## Conventions this skeleton must follow (from CLAUDE.md)

- Repos are a constructor function returning a `NamedTuple` of async closures
  over `db`, with a `Protocol`/`NamedTuple` pair defining the interface —
  not a class. See `src/modules/users/repositories.py`.
- Every repo function that touches Mongo is wrapped in `@handle_mongo_error`
  from `src.mongodb.exceptions`.
- Models extend `MongoModel` (`src.mongodb.models`) and use `utcnow()` for
  timestamps — never `datetime.utcnow()`.
- Domain errors are `BaseDomainException` subclasses in `exceptions.py`, not
  bare `HTTPException`.
- `service.py` takes its dependencies (repo, etc.) as explicit keyword args,
  not by importing them directly — keeps it callable/testable without FastAPI.
- `router.py` stays thin: parse/validate via `Depends`, call `service.py`,
  return. No business logic in the router.
- `dependencies.py` exposes `Depends`-based providers as `XxxDep = Annotated[...]`
  type aliases.
- Use `scope_logger()` (no args) for logging, never stdlib `logging` directly.
- New routers are registered manually in `create_app()` — nothing is
  auto-discovered.

## Templates

### `models.py`

```python
from datetime import datetime

from pydantic import Field

from src.mongodb.models import MongoModel, utcnow


class {Model}(MongoModel):
    # TODO: replace with real fields
    name: str
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
```

### `repositories.py`

```python
from collections.abc import Awaitable, Callable
from typing import NamedTuple, Protocol

from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from src.modules.{module}.models import {Model}
from src.mongodb.exceptions import handle_mongo_error
from src.mongodb.models import utcnow

COLLECTION = "{collection}"


# === The contract / Interface ==================
class {Model}Repo(NamedTuple):

    get_by_id: Callable[[str], Awaitable[{Model} | None]]
    create: Callable[[{Model}], Awaitable[{Model} | None]]


# === {Model} Repository ==================
def mongo_{module_singular}_repo(db: AsyncDatabase) -> {Model}Repo:
    col = db[COLLECTION]

    @handle_mongo_error
    async def get_by_id(id: str) -> {Model} | None:
        return {Model}.from_mongo(await col.find_one({{"_id": id}}))

    @handle_mongo_error
    async def create(item: {Model}) -> {Model} | None:
        doc = item.to_mongo()
        await col.insert_one(doc)
        return {Model}.from_mongo(doc)

    return {Model}Repo(get_by_id=get_by_id, create=create)
```

Note: `Protocol` import stays only if a callable needs keyword-only args (see
`ListRecent` in `users/repositories.py`); drop it if every method fits a
plain `Callable[[...], Awaitable[...]]` signature.

### `exceptions.py`

```python
from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.status_codes import StatusCode


class {Model}NotFound(BaseDomainException):
    message = "There is no existing {module_singular}"
    internal_code = "{MODULE_UPPER}_NOT_FOUND"
    status_code = StatusCode.NOT_FOUND
```

### `dependencies.py`

```python
from typing import Annotated

from fastapi import Depends

from src.modules.{module}.exceptions import {Model}NotFound
from src.modules.{module}.repositories import {Model}Repo, mongo_{module_singular}_repo
from src.mongodb.dependencies import DatabaseDep


def get_{module_singular}_repo(db: DatabaseDep) -> {Model}Repo:
    return mongo_{module_singular}_repo(db)


{Model}RepoDep = Annotated[{Model}Repo, Depends(get_{module_singular}_repo)]


async def get_valid_{module_singular}(*, repo: {Model}Repo, id: str):
    item = await repo.get_by_id(id)
    if item is None:
        raise {Model}NotFound()
    return item
```

### `schemas.py`

```python
from pydantic import BaseModel


class Create{Model}Request(BaseModel):
    # TODO: request body fields
    name: str


class {Model}Response(BaseModel):
    # TODO: response fields (may differ from the stored model)
    id: str
    name: str
```

### `service.py`

```python
from src.modules.{module}.models import {Model}
from src.modules.{module}.repositories import {Model}Repo
from src.modules.{module}.schemas import Create{Model}Request
from src.logging import scope_logger

logger = scope_logger()


async def create_{module_singular}(
    *,
    repo: {Model}Repo,
    payload: Create{Model}Request,
) -> {Model}:
    item = await repo.create({Model}(name=payload.name))
    assert item is not None
    logger.info(f"created {module_singular} {{item.id}}")
    return item
```

### `router.py`

```python
from fastapi import APIRouter, status

from src.modules.{module}.dependencies import {Model}RepoDep
from src.modules.{module}.schemas import Create{Model}Request, {Model}Response
from src.modules.{module} import service as {module}_service

router = APIRouter()


@router.post("", response_model={Model}Response, status_code=status.HTTP_201_CREATED)
async def create_{module_singular}(
    payload: Create{Model}Request,
    repo: {Model}RepoDep,
) -> {Model}Response:
    item = await {module}_service.create_{module_singular}(repo=repo, payload=payload)
    return {Model}Response(id=item.id, name=item.name)
```

### `src/app.py` registration

Add near the other module imports/includes (uncomment the pattern already
used for `users_router` if that's the first real module being wired in):

```python
from src.modules.{module}.router import router as {module}_router
...
app.include_router({module}_router, prefix="/api/{module}", tags=["{Model}"])
```
