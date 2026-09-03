import pytest

from src.tests.database.client import client as mongo_client
from conftest import TEST_DB_NAME


class TestCreateTripProject:

    @pytest.mark.asyncio
    async def test_create_trip_project(self, client):
        response = await client.post(
            "/api/trip-projects",
            headers={"Authorization": "Bearer alice"},
            json={
                "name": "Japan Trip",
                "description": "Test trip",
            },
        )

        assert response.status_code == 201

        database = mongo_client[TEST_DB_NAME]
        collection = database["trip_projects"]

        saved_project = collection.find_one({"name": "Japan Trip"})

        assert saved_project is not None
        assert saved_project["name"] == "Japan Trip"
        assert saved_project["description"] == "Test trip"
