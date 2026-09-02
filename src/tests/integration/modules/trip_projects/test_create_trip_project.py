from pymongo import MongoClient

from src.tests.conftest import TEST_DB_NAME, TEST_MONGO_URI


def test_create_trip_project(client, require_local_mongodb):
    response = client.post(
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

        # Replace "trip_projects" if your repository uses another collection name.
        saved_project = database["trip_projects"].find_one({"name": "Japan Trip"})

        assert saved_project is not None
        assert saved_project["description"] == "Test trip"
    finally:
        mongo.close()
