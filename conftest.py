import os
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

pytest_plugins = ("src.tests.fixtures.users", "src.tests.fixtures.firebase")

TEST_MONGO_URI = "mongodb://localhost:27017/"
TEST_DB_NAME = "maketravo_test"

# These names must match Settings in src/config.py.
os.environ["MONGODB_URI"] = TEST_MONGO_URI
os.environ["MONGODB_DB_NAME"] = TEST_DB_NAME


@pytest_asyncio.fixture
async def local_database() -> AsyncIterator[AsyncDatabase]:
    mongo = AsyncMongoClient(
        TEST_MONGO_URI,
        serverSelectionTimeoutMS=1000,
    )

    try:
        await mongo.admin.command("ping")
        yield mongo[TEST_DB_NAME]
    finally:
        await mongo.close()


@pytest_asyncio.fixture()
async def client(local_database: AsyncDatabase) -> AsyncIterator[AsyncClient]:
    from src.app import create_app
    from src.mongodb.dependencies import get_database
    from src.firebase.dependencies import get_firebase_auth
    from src.tests.fixtures.firebase import FakeFirebaseAuth

    app = create_app()
    app.dependency_overrides[get_firebase_auth] = lambda: FakeFirebaseAuth()
    app.dependency_overrides[get_database] = lambda: local_database

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client


# Start of session hook to set up the test database before the test session starts.
def pytest_sessionstart(session: pytest.Session) -> None:
    """Set up the test database before the test session starts."""

    from src.tests.database.users import create_existing_users

    create_existing_users()


# When tests end
def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int | pytest.ExitCode,
) -> None:
    """Clean up the test database after the test session is complete."""
    from src.tests.database.client import client

    client.drop_database(TEST_DB_NAME)
