import pytest
from async_asgi_testclient import TestClient

from src.nlp.services.recommendation_generation import (
    dynamic_score_entities,
    recommend_technologies,
)


@pytest.fixture
async def tech_entities_fixture():
    """Async fixture to simulate or mock the expected output of load_tech_entities()."""

    return {
        "MySQL": {"category": "Database", "patterns": [], "score": 1},
        "MongoDB": {"category": "Database", "patterns": [], "score": 0.9},
    }


@pytest.mark.asyncio
async def test_dynamic_score_entities(client: TestClient, tech_entities_fixture):
    """Test case for dynamic_score_entities function."""

    entities = [
        {"entity": "MySQL", "category": "Database"},
        {"entity": "MongoDB", "category": "Database"},
    ]
    topic_keywords = ["databases", "schemas", "tables"]
    user_input = "In comparing database management systems, we're evaluating the performance and features of MySQL versus MongoDB to determine the best fit."
    tech_entities = await tech_entities_fixture
    sorted_entities = dynamic_score_entities(entities, topic_keywords, user_input, tech_entities)
    assert sorted_entities[0]["entity_name"] == "MySQL"
    assert sorted_entities[1]["entity_name"] == "MongoDB"


def test_recommend_technologies():
    """Test case for recommend_technologies function."""

    entities = [
        {"entity_name": "React", "score": 0.9, "category": "Frontend"},
        {"entity_name": "NodeJS", "score": 0.8, "category": "Backend"},
    ]
    recommendations = recommend_technologies(entities)
    assert recommendations[0]["recommendation"] == "React"
    assert recommendations[1]["recommendation"] == "NodeJS"
