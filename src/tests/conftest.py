import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

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


class FakeFirebaseAuth:
    def verify_id_token(self, token: str) -> dict[str, str]:
        return {
            "uid": f"user-{token}",
            "email": f"{token}@example.com",
        }


@pytest.fixture
def client() -> Iterator[TestClient]:
    from src.app import create_app
    from src.firebase.dependencies import get_firebase_auth

    app = create_app()
    app.dependency_overrides[get_firebase_auth] = lambda: FakeFirebaseAuth()

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client

    app.dependency_overrides.clear()
