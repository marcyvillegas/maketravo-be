import os
import sys
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from pymongo import MongoClient

pytest_plugins = ("src.tests.fixtures.users", "src.tests.fixtures.firebase")

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

TEST_MONGO_URI = "mongodb://localhost:27017/"
TEST_DB_NAME = "maketravo_test"

# These names must match Settings in src/config.py.
os.environ["MONGODB_URI"] = TEST_MONGO_URI
os.environ["MONGODB_DB_NAME"] = TEST_DB_NAME


# Tests explicitly request this fixture when they require local MongoDB.
@pytest.fixture(scope="session")
def require_local_mongodb() -> Iterator[None]:
    mongo = MongoClient(
        TEST_MONGO_URI,
        serverSelectionTimeoutMS=1000,
    )

    try:
        mongo.admin.command("ping")
        yield
    finally:
        mongo.close()


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    from src.app import create_app
    from src.firebase.dependencies import get_firebase_auth
    from src.tests.fixtures.firebase import FakeFirebaseAuth

    app = create_app()
    app.dependency_overrides[get_firebase_auth] = lambda: FakeFirebaseAuth()

    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client

    app.dependency_overrides.clear()


def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int | pytest.ExitCode,
) -> None:
    """Clean up the test database after the test session is complete."""
    mongo = MongoClient(TEST_MONGO_URI)
    try:
        mongo.drop_database(TEST_DB_NAME)
    finally:
        mongo.close()
