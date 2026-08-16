"""
Owns exactly one AsyncMongoClient for this process.
Deliberately NO module-level instance
"""

from typing import Any

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from src.config import Settings
from src.mongodb.exceptions import DatabaseUnavailable
from src.logging import scope_logger

logger = scope_logger()


class MongoConnection:

    def __init__(self, settings: Settings):
        self._uri = settings.MONGODB_URI.get_secret_value()
        self._db_name = settings.MONGODB_DB_NAME
        self._options: dict[str, Any] = {
            "maxPoolSize": settings.MONGODB_MAX_POOL_SIZE,
            "minPoolSize": settings.MONGODB_MIN_POOL_SIZE,
            "serverSelectionTimeoutMS": settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            "connectTimeoutMS": settings.MONGODB_CONNECT_TIMEOUT_MS,
            "socketTimeoutMS": settings.MONGODB_SOCKET_TIMEOUT_MS,
            "retryWrites": True,
            "retryReads": True,
            "tz_aware": True,
            "uuidRepresentation": "standard",
            "appname": "maketravo-be",  # for Atlas monitoring
        }
        self._client: AsyncMongoClient | None = None

    # === Lifecyle =====================================================

    async def connect(self) -> None:
        """Idempotent — safe to call twice."""
        if self._client is not None:
            return

        client = AsyncMongoClient(self._uri, **self._options)

        try:
            await client.admin.command("ping")
        except Exception as e:
            await client.close()
            logger.critical(f"MongoDB unreachable at startup:{type(e).__name__}")
            raise DatabaseUnavailable() from e

        self._client = client
        logger.info(f"MongoDB connected (db={self._db_name})")

    async def disconnect(self) -> None:
        if self._client is None:
            return
        # NOTE: close() is a coroutine in the async API, unlike sync PyMongo.
        # A bare self._client.close() warns about an un-awaited coroutine
        # and closes nothing.
        await self._client.close()
        self._client = None
        logger.info("MongoDB disconnected")

    # === Accessors =====================================================

    @property
    def client(self) -> AsyncMongoClient:
        if self._client is None:
            raise DatabaseUnavailable(message="Database is not connected")
        return self._client

    @property
    def db(self) -> AsyncDatabase:
        return self.client[self._db_name]

    async def ping(self) -> bool:
        """Liveness probe for /health."""
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False
