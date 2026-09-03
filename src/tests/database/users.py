from polyfactory.factories.pydantic_factory import ModelFactory

from src.modules.users.models import User
from src.tests.database.client import client
from conftest import TEST_DB_NAME


class UserFactory(ModelFactory[User]):
    __model__ = User


user_1 = UserFactory.build(
    firebase_uid="user123",
    email="alice@example.com",
    display_name="Alice",
    photo_url="https://example.com/alice.jpg",
).to_mongo()


def create_existing_users():
    database = client[TEST_DB_NAME]
    collection = database["users"]

    collection.insert_one(user_1)
