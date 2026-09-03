from pymongo import MongoClient
import pytest


from src.tests.conftest import TEST_DB_NAME, TEST_MONGO_URI


class TestCreateTripProject:
    @pytest.mark.asyncio
    async def test_create_trip_project(self, client, require_local_mongodb):
        response = await client.post(
            "/api/trip-projects",
            headers={"Authorization": "Bearer alice"},
            json={
                "name": "Japan Trip",
                "description": "Test trip",
            },
        )

        assert response.status_code == 201

        mongo = MongoClient(TEST_MONGO_URI)
        try:
            database = mongo[TEST_DB_NAME]
            collection = database["trip_projects"]

            saved_project = collection.find_one({"name": "Japan Trip"})

            assert saved_project is not None
            assert saved_project["name"] == "Japan Trip"
            assert saved_project["description"] == "Test trip"
        finally:
            # collection.delete_one({"name": "Japan Trip"})
            mongo.close()
