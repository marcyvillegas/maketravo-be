import pytest

from src.modules.users.exceptions import UserAlreadyExists

import logging

logger = logging.getLogger(__name__)


class TestExistingUser:

    @pytest.mark.asyncio
    async def test_existing_user(self, client, fake_auth, get_existing_user_1):
        # Configure the fake Firebase auth to simulate an existing user
        fake_auth.configure_user(
            uid_prefix=get_existing_user_1["firebase_uid"],
            email_domain=get_existing_user_1["email"].split("@")[1],
        )

        # Simulate a request with a token for the existing user
        token = "existing_user_token"
        response = await client.post(
            "/api/users",
            json={
                "email": get_existing_user_1["email"],
                "display_name": "Alice",
                "photo_url": "https://example.com/alice.jpg",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        logger.info(f"Response JSON: {response.json()}")

        # Assert that the response is successful and contains the expected data
        assert response.status_code == UserAlreadyExists.status_code
        assert response.json()["success"] == False
        assert response.json()["error"]["message"] == UserAlreadyExists.message
        assert response.json()["error"]["code"] == UserAlreadyExists.internal_code
        assert response.json()["error"]["trace_id"] is not None
