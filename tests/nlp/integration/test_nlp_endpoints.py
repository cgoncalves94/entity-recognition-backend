import pytest
from async_asgi_testclient import TestClient
from fastapi import status

from src.auth import jwt


@pytest.fixture
def auth_token():
    test_user = {"_id": "test_user_id", "email": "test@example.com", "is_admin": False}
    access_token = jwt.create_access_token(user=test_user)
    return access_token


@pytest.mark.asyncio
async def test_process_endpoint(client: TestClient, auth_token: str):
    input_data = {"texts": ["Create a workflow for AWS and a express mongodb starter."]}

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post("/nlp/process/", json=input_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert "extracted_entities" in response.json()[0]


@pytest.mark.asyncio
async def test_match_blueprints_endpoint(client: TestClient, auth_token: str):
    recommendations = [
        {
            "input_text": "Create a workflow for AWS and a express mongodb starter.",
            "predicted_topic_name": "Cloud Infrastructure",
            "extracted_entities": [
                {"category": "Backend", "entity_name": "Express.js", "score": 0.8},
                {"category": "Database", "entity_name": "MongoDB", "score": 0.9},
            ],
            "recommendations": [{"category": "Backend", "recommendation": "Express.js"}, {"category": "Database", "recommendation": "MongoDB"}],
        }
    ]

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post("/nlp/match-blueprints/", json=recommendations, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert "matched_blueprints" in response.json()[0]
    assert len(response.json()[0]["matched_blueprints"]) > 0
