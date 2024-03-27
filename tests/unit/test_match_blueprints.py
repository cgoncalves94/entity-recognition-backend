import pytest

from src.nlp.services.blueprint_matching import load_blueprints_corpus, match_blueprints


@pytest.fixture
async def blueprints_corpus():
    """Async fixture to load the blueprints_corpus from the JSON file."""

    return await load_blueprints_corpus()


@pytest.fixture
def nlp_output():
    """Fixture for the NLP output with extracted entities and recommendations."""

    return [
        {
            "extracted_entities": [
                {"entity_name": "GitHub Actions", "category": "CI/CD"},
                {"entity_name": "AWS", "category": "Cloud Service Provider"},
                {"entity_name": "Express.js", "category": "Backend"},
            ],
            "recommendations": [
                {"category": "CI/CD", "recommendation": "GitHub Actions"},
                {"category": "Cloud Service Provider", "recommendation": "AWS"},
                {"category": "Backend", "recommendation": "Express.js"},
            ],
        }
    ]


@pytest.mark.asyncio
async def test_match_blueprints_single_recommendation(blueprints_corpus, nlp_output):
    """Tests that the match_blueprints() function correctly matches a single recommendation."""

    matched_blueprints = match_blueprints(nlp_output, await blueprints_corpus)

    # Assert that the expected blueprint is matched
    assert "backend" in matched_blueprints
    assert matched_blueprints["backend"][0]["name"] == "Node.js Express Starter"


@pytest.mark.asyncio
async def test_match_blueprints_multiple_recommendations(blueprints_corpus, nlp_output):
    """Tests that the match_blueprints() function correctly matches multiple recommendations."""

    matched_blueprints = match_blueprints(nlp_output, await blueprints_corpus)

    # Flatten the matched blueprints for easier assertion
    flattened_matched_blueprints = [blueprint for category_blueprints in matched_blueprints.values() for blueprint in category_blueprints]

    expected_blueprint_names = {"Node.js Express Starter", "AWS Configure"}

    # Verify each expected blueprint is present by name
    for expected_name in expected_blueprint_names:
        assert any(
            blueprint["name"] == expected_name for blueprint in flattened_matched_blueprints
        ), f"Expected blueprint '{expected_name}' not found in matched blueprints."


@pytest.mark.asyncio
async def test_match_blueprints_no_matching_blueprints(blueprints_corpus):
    """Tests that the match_blueprints() function correctly handles no matching blueprints."""

    nlp_output = [
        {
            "recommendations": [{"recommendation": "Unknown Technology"}],
            "extracted_entities": [],
        }
    ]

    # Await the blueprints_corpus coroutine to get the actual data
    blueprints_data = await blueprints_corpus

    matched_blueprints = match_blueprints(nlp_output, blueprints_data)

    # Assert that no blueprints are matched
    assert matched_blueprints == {}
