import pytest
from src.tests.database.users import user_1


@pytest.fixture()
def get_existing_user_1():
    return user_1
