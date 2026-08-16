from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import Settings, get_settings
from src.mongodb.connection import MongoConnection

# from src.database.indexes import ensure_indexes
# from src.health.router import router as health_router
from src.modules.sessions.router import router as sessions_router
from src.shared.exceptions.global_exception import register_exception_handlers

# from src.users.router import router as users_router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """One Mongo connection per process — opened at boot, closed at exit."""

        # ---- startup ----
        mongo = MongoConnection(settings)
        await mongo.connect()

        # if settings.MONGODB_AUTO_CREATE_INDEXES:
        #     await ensure_indexes(mongo.db)

        # The handoff: lifespan locals aren't visible to request handlers,
        # so park them on app.state where a dependency can reach them.
        app.state.mongo = mongo
        app.state.settings = settings

        try:
            yield  # ← app serves requests for as long as it lives
        finally:
            # ---- shutdown ---- (finally, so it always runs)
            await mongo.disconnect()

    app = FastAPI(
        docs_url="/api-docs",
        redoc_url=None,
        summary="MakeTravo Endpoints",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # never ["*"] with credentials
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Global exceptions
    register_exception_handlers(app)

    # Routes
    # app.include_router(health_router, tags=["Health"])
    app.include_router(sessions_router, prefix="/api/sessions", tags=["Sessions"])
    # app.include_router(users_router, prefix="/api/users", tags=["Users"])

    return app
