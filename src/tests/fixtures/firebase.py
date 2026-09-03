import pytest


class FakeFirebaseAuth:
    def __init__(self):
        # Default user configuration
        self.uid_prefix = "user123"
        self.email_domain = "example.com"

    def configure_user(self, uid_prefix: str, email_domain: str):
        """Helper method for devs to change user type dynamically."""
        self.uid_prefix = uid_prefix
        self.email_domain = email_domain

    def verify_id_token(self, token: str) -> dict[str, str]:

        return {
            "uid": f"{self.uid_prefix}",
            "email": f"{token}@{self.email_domain}",
        }


@pytest.fixture
def fake_auth() -> FakeFirebaseAuth:
    return FakeFirebaseAuth()
