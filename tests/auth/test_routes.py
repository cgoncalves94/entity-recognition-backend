import pytest
from async_asgi_testclient import TestClient
from fastapi import status

from src.auth.constants import ErrorCode
from src.auth.dependencies import service


@pytest.mark.asyncio
async def test_register(client: TestClient):
    """Tests user registration."""
    
    resp = await client.post(
        "/auth/users",
        json={
            "email": "test_user@example.com",
            "password": "123Aa!",
        },
    )
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp_json == {"email": "test_user@example.com"}


@pytest.mark.asyncio
async def test_login_endpoint(client: TestClient, user_cleanup) -> None:
    """Tests user login and token generation."""
    
    # Set up user data (replace with your actual user creation logic)
    user_email = "test_user@example.com"
    user_password = "123Aa!"
    await client.post(
        "/auth/users",
        json={"email": user_email, "password": user_password},
    )

    response = await client.post(
        "/auth/users/tokens",
        json={"email": user_email, "password": user_password},
    )

    assert response.status_code == status.HTTP_200_OK

    
@pytest.mark.asyncio
async def test_register_email_taken(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests user registration when the email is already taken."""
    
    async def fake_getter(*args, **kwargs):
        """Fake getter function to simulate a user already existing in the database."""
        return True

    # Patch the get_user_by_email function to return True
    monkeypatch.setattr(service, "get_user_by_email", fake_getter)

    # Attempt to register a user with an email that already exists
    resp = await client.post(
        "/auth/users",
        json={
            "email": "test_user@example.com",
            "password": "123Aa!",
        },
    )
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_json["detail"] == ErrorCode.EMAIL_TAKEN
    
