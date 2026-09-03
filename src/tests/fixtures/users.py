from pymongo import MongoClient
import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from src.modules.users.models import User
from src.tests.conftest import TEST_DB_NAME, TEST_MONGO_URI


class UserFactory(ModelFactory[User]):
    __model__ = User


user_1 = UserFactory.build(
    firebase_uid="user123",
    email="alice@example.com",
    display_name="Alice",
    photo_url="https://example.com/alice.jpg",
).to_mongo()


@pytest.fixture(scope="session", autouse=True)
def create_existing_users():

    mongo = MongoClient(TEST_MONGO_URI)
    try:
        database = mongo[TEST_DB_NAME]
        collection = database["users"]

        collection.insert_one(user_1)

    finally:
        mongo.close()


@pytest.fixture()
def get_existing_user_1():
    return user_1
